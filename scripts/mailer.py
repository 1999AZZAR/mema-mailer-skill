#!/usr/bin/env python3
"""
Mema Mailer - Robust email delivery via Resend API.

Features:
  - Jinja2 template rendering with inheritance
  - Input validation (emails, template existence)
  - Retry with exponential backoff on transient failures
  - Rate limit awareness (429 handling)
  - Dry-run mode (render only, no send)
  - Batch sending (multiple recipients)
  - Template listing
  - Context from JSON string or file
  - Timeout and connection pooling
"""

import os
import sys
import re
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Optional

import requests
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "assets" / "templates"
DEFAULT_FROM = os.getenv("SENDER_EMAIL", "mema@glassgallery.my.id")
API_URL = "https://api.resend.com/emails"
MAX_RETRIES = 3
RETRY_BACKOFF = [0.5, 1.5, 4.0]  # seconds
REQUEST_TIMEOUT = 30  # seconds

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("mema-mailer")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def validate_email(addr: str) -> bool:
    return bool(EMAIL_RE.match(addr))


def parse_emails(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    return [e.strip() for e in raw.split(",") if e.strip()]


def validate_emails(addrs: list[str], label: str) -> list[str]:
    invalid = [a for a in addrs if not validate_email(a)]
    if invalid:
        raise ValueError(f"Invalid {label} email(s): {', '.join(invalid)}")
    return addrs


# ---------------------------------------------------------------------------
# MemaMailer
# ---------------------------------------------------------------------------
class MemaMailer:
    """Resend email sender with Jinja2 templating."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        sender: Optional[str] = None,
        template_dir: Optional[Path] = None,
    ):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        if not self.api_key:
            raise ValueError(
                "RESEND_API_KEY not found. Set it in .env or pass explicitly."
            )
        self.sender = sender or DEFAULT_FROM
        self.template_dir = Path(template_dir or TEMPLATE_DIR)

        if not self.template_dir.is_dir():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,  # email HTML is trusted
            keep_trailing_newline=True,
        )

    # ------------------------------------------------------------------
    # Template helpers
    # ------------------------------------------------------------------
    def list_templates(self) -> list[str]:
        """Return sorted list of available template names (without .html)."""
        return sorted(
            p.stem
            for p in self.template_dir.glob("*.html")
            if not p.name.startswith("_")
        )

    def has_template(self, name: str) -> bool:
        return (self.template_dir / f"{name}.html").is_file()

    def render(self, template_name: str, context: Optional[dict] = None) -> str:
        """Render a template to HTML string. Raises on missing/broken template."""
        context = context or {}
        tpl = self.env.get_template(f"{template_name}.html")
        return tpl.render(**context)

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------
    def send(
        self,
        to_emails: list[str],
        subject: str,
        template_name: str,
        context: Optional[dict] = None,
        cc_emails: Optional[list[str]] = None,
        bcc_emails: Optional[list[str]] = None,
        reply_to: Optional[str] = None,
        dry_run: bool = False,
    ) -> dict:
        """
        Render template and send via Resend.

        Returns:
            {"status": "success", "message": "...", "resend_id": "..."}
            or
            {"status": "error", "message": "...", "code": "..."}
        """
        # -- Validate inputs --
        if not to_emails:
            return {"status": "error", "message": "No recipients specified"}
        if not subject:
            return {"status": "error", "message": "Subject is required"}

        validate_emails(to_emails, "to")
        if cc_emails:
            validate_emails(cc_emails, "cc")
        if bcc_emails:
            validate_emails(bcc_emails, "bcc")

        if not self.has_template(template_name):
            available = ", ".join(self.list_templates())
            return {
                "status": "error",
                "message": f"Template '{template_name}' not found. Available: {available}",
            }

        # -- Render --
        try:
            html = self.render(template_name, context)
        except TemplateNotFound:
            return {"status": "error", "message": f"Template '{template_name}' not found"}
        except TemplateSyntaxError as e:
            return {"status": "error", "message": f"Template syntax error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Template render failed: {e}"}

        if dry_run:
            return {
                "status": "dry_run",
                "message": f"Rendered {template_name} ({len(html)} bytes)",
                "html_preview": html[:500] + "..." if len(html) > 500 else html,
                "to": to_emails,
                "subject": subject,
            }

        # -- Build payload --
        payload = {
            "from": f"Mema AI <{self.sender}>",
            "to": to_emails,
            "subject": subject,
            "html": html,
        }
        if cc_emails:
            payload["cc"] = cc_emails
        if bcc_emails:
            payload["bcc"] = bcc_emails
        if reply_to:
            payload["reply_to"] = reply_to

        # -- Send with retries --
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                )

                # Success
                if resp.status_code in (200, 201):
                    data = resp.json()
                    log.info(
                        "Sent to %s | id=%s",
                        ", ".join(to_emails),
                        data.get("id", "?"),
                    )
                    return {
                        "status": "success",
                        "message": f"Email sent to {', '.join(to_emails)}",
                        "resend_id": data.get("id"),
                    }

                # Rate limited — retry after backoff
                if resp.status_code == 429:
                    retry_after = float(resp.headers.get("Retry-After", RETRY_BACKOFF[attempt]))
                    log.warning("Rate limited. Retrying in %.1fs (attempt %d/%d)", retry_after, attempt + 1, MAX_RETRIES)
                    time.sleep(retry_after)
                    continue

                # Client error (4xx except 429) — don't retry
                if 400 <= resp.status_code < 500:
                    error_data = resp.json() if resp.content else {}
                    error_msg = error_data.get("message", resp.text)
                    return {
                        "status": "error",
                        "message": f"API error ({resp.status_code}): {error_msg}",
                        "code": error_data.get("name", "unknown"),
                    }

                # Server error (5xx) — retry
                last_error = f"Server error {resp.status_code}"
                log.warning("Server error %d. Attempt %d/%d", resp.status_code, attempt + 1, MAX_RETRIES)
                time.sleep(RETRY_BACKOFF[attempt])

            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                log.warning("Timeout. Attempt %d/%d", attempt + 1, MAX_RETRIES)
                time.sleep(RETRY_BACKOFF[attempt])
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {e}"
                log.warning("Connection error. Attempt %d/%d", attempt + 1, MAX_RETRIES)
                time.sleep(RETRY_BACKOFF[attempt])
            except requests.exceptions.RequestException as e:
                return {"status": "error", "message": f"Request failed: {e}"}

        return {
            "status": "error",
            "message": f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}",
        }

    # ------------------------------------------------------------------
    # Batch
    # ------------------------------------------------------------------
    def send_batch(
        self,
        recipients: list[str],
        subject: str,
        template_name: str,
        context: Optional[dict] = None,
        cc_emails: Optional[list[str]] = None,
        bcc_emails: Optional[list[str]] = None,
        dry_run: bool = False,
    ) -> list[dict]:
        """Send to multiple recipients individually (not as a group)."""
        results = []
        for addr in recipients:
            result = self.send(
                to_emails=[addr],
                subject=subject,
                template_name=template_name,
                context=context,
                cc_emails=cc_emails,
                bcc_emails=bcc_emails,
                dry_run=dry_run,
            )
            result["recipient"] = addr
            results.append(result)
            # Small delay between sends to avoid rate limits
            if not dry_run and len(recipients) > 1:
                time.sleep(0.1)
        return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Mema Mailer — send templated emails via Resend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --to user@example.com --subject "Hello" --template default --context '{"name":"World"}'
  %(prog)s --to user@example.com --subject "Alert" --template alert --context-file alert.json
  %(prog)s --list-templates
  %(prog)s --to user@example.com --subject "Test" --template basic --dry-run
        """,
    )
    p.add_argument("--to", help="Comma-separated recipient emails")
    p.add_argument("--cc", help="Comma-separated CC emails")
    p.add_argument("--bcc", help="Comma-separated BCC emails")
    p.add_argument("--reply-to", help="Reply-To address")
    p.add_argument("--subject", help="Email subject")
    p.add_argument("--template", default="default", help="Template name (default: default)")
    p.add_argument("--context", help="JSON string of template variables")
    p.add_argument("--context-file", help="Path to JSON file with template variables")
    p.add_argument("--dry-run", action="store_true", help="Render only, do not send")
    p.add_argument("--list-templates", action="store_true", help="List available templates and exit")
    p.add_argument("--batch", help="Comma-separated list of recipients for individual sends")
    p.add_argument("--api-key", help="Resend API key (overrides env)")
    p.add_argument("--sender", help="Sender email (overrides env)")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    # -- List templates --
    if args.list_templates:
        try:
            mailer = MemaMailer(api_key=args.api_key or "dummy", sender=args.sender)
            templates = mailer.list_templates()
            print(f"Available templates ({len(templates)}):")
            for t in templates:
                print(f"  - {t}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # -- Require --to and --subject for sending --
    if not args.to and not args.batch:
        parser.error("--to or --batch is required")
    if not args.subject:
        parser.error("--subject is required")

    # -- Load context --
    context = {}
    if args.context_file:
        path = Path(args.context_file)
        if not path.is_file():
            print(f"Error: context file not found: {path}", file=sys.stderr)
            sys.exit(1)
        with open(path) as f:
            context = json.load(f)
    elif args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON in --context: {e}", file=sys.stderr)
            sys.exit(1)

    # -- Init mailer --
    try:
        mailer = MemaMailer(api_key=args.api_key, sender=args.sender)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # -- Batch mode --
    if args.batch:
        recipients = parse_emails(args.batch)
        validate_emails(recipients, "batch")
        results = mailer.send_batch(
            recipients=recipients,
            subject=args.subject,
            template_name=args.template,
            context=context,
            cc_emails=parse_emails(args.cc),
            bcc_emails=parse_emails(args.bcc),
            dry_run=args.dry_run,
        )
        print(json.dumps(results, indent=2))
        failed = [r for r in results if r["status"] != "success"]
        sys.exit(1 if failed else 0)
        return

    # -- Single send --
    to_list = parse_emails(args.to)
    try:
        validate_emails(to_list, "to")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    result = mailer.send(
        to_emails=to_list,
        subject=args.subject,
        template_name=args.template,
        context=context,
        cc_emails=parse_emails(args.cc),
        bcc_emails=parse_emails(args.bcc),
        reply_to=args.reply_to,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] in ("success", "dry_run") else 1)


if __name__ == "__main__":
    main()
