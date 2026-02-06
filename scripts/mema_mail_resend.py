import os
import sys
import argparse
import json
import requests
from jinja2 import Environment, FileSystemLoader

# --- Config ---
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
SENDER_EMAIL = "mema@glassgallery.my.id"
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

class MemaMailer:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def send(self, to_email, subject, template_name, context=None):
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
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            response = requests.post(url, headers=headers, json=data)
            resp_data = response.json()

            if response.status_code in [200, 201]:
                return {"status": "success", "message": f"Email sent via Resend to {to_email}", "resend_id": resp_data.get("id")}
            else:
                return {"status": "error", "message": resp_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mema Mailer CLI (Resend Version)")
    parser.add_argument("--to", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--template", default="default")
    parser.add_argument("--context", help="JSON string for template variables")

    args = parser.parse_args()
    context_data = json.loads(args.context) if args.context else {}

    mailer = MemaMailer()
    result = mailer.send(args.to, args.subject, args.template, context_data)
    print(json.dumps(result, indent=2))
