import os
import sys
import argparse
import json
import requests
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Config ---
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../assets/templates")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "mema@glassgallery.my.id")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

class MemaMailer:
    def __init__(self):
        if not RESEND_API_KEY:
            raise ValueError("RESEND_API_KEY not found in environment")
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def send(self, to_emails, subject, template_name, context=None, cc_emails=None, bcc_emails=None):
        context = context or {}
        try:
            template = self.env.get_template(f"{template_name}.html")
            html_content = template.render(**context)

            # Send via Resend API
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "from": f"Mema AI <{SENDER_EMAIL}>",
                "to": to_emails,
                "subject": subject,
                "html": html_content
            }
            
            if cc_emails:
                data["cc"] = cc_emails
            if bcc_emails:
                data["bcc"] = bcc_emails
            
            response = requests.post(url, headers=headers, json=data)
            resp_data = response.json()

            if response.status_code in [200, 201]:
                return {
                    "status": "success", 
                    "message": f"Email sent to {', '.join(to_emails)}", 
                    "resend_id": resp_data.get("id")
                }
            else:
                return {"status": "error", "message": resp_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mema Mailer CLI (Resend Version)")
    parser.add_argument("--to", required=True, help="Comma separated recipient emails")
    parser.add_argument("--cc", help="Comma separated CC emails")
    parser.add_argument("--bcc", help="Comma separated BCC emails")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--template", default="default")
    parser.add_argument("--context", help="JSON string for template variables")

    args = parser.parse_args()
    context_data = json.loads(args.context) if args.context else {}
    
    # Process email lists (comma separated)
    to_list = [e.strip() for e in args.to.split(',') if e.strip()]
    cc_list = [e.strip() for e in args.cc.split(',') if e.strip()] if args.cc else []
    bcc_list = [e.strip() for e in args.bcc.split(',') if e.strip()] if args.bcc else []

    mailer = MemaMailer()
    result = mailer.send(to_list, args.subject, args.template, context_data, cc_list, bcc_list)
    print(json.dumps(result, indent=2))
