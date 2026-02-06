import os
import sys
import argparse
import subprocess
from jinja2 import Environment, FileSystemLoader

# --- Config ---
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
SENDER_EMAIL = "mema@glassgallery.my.id"

class MemaMailer:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def send(self, to_email, subject, template_name, context=None):
        context = context or {}
        try:
            template = self.env.get_template(f"{template_name}.html")
            html_content = template.render(**context)

            # Construct the email message
            message = (
                f"From: Mema AI <{SENDER_EMAIL}>\n"
                f"To: {to_email}\n"
                f"Subject: {subject}\n"
                f"MIME-Version: 1.0\n"
                f"Content-Type: text/html; charset=utf-8\n\n"
                f"{html_content}"
            )

            # Send via msmtp
            process = subprocess.Popen(
                ["msmtp", "-a", "default", to_email],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=message)

            if process.returncode == 0:
                return {"status": "success", "message": f"Email sent to {to_email}"}
            else:
                return {"status": "error", "message": stderr}

        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mema Mailer CLI")
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--template", default="default")
    # Simple JSON context for dynamic values
    parser.add_argument("--context", help="JSON string for template variables")

    args = parser.parse_args()
    import json
    context_data = json.loads(args.context) if args.context else {}

    mailer = MemaMailer()
    result = mailer.send(args.to, args.subject, args.template, context_data)
    print(json.dumps(result, indent=2))
