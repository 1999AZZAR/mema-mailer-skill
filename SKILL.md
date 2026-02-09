---
name: mema-mailer
description: Professional email delivery system using the Resend API and Python-based HTML templating (Jinja2). Use when user asks to "send email", "notify me", "send report".
---

# Mema Mailer

## Setup
1. Copy `.env.example` to `.env`.
2. Set `RESEND_API_KEY` (from Resend.com).
3. Ensure Python dependencies (`jinja2`, `requests`, `python-dotenv`) are installed.

## Usage
- **Role**: Executive Assistant.
- **Trigger**: "Email me this", "Send daily report".
- **Output**: Sent email status + Resend delivery ID.

## Capabilities
1. **Templating**: Responsive HTML emails using Jinja2 (`assets/templates`).
2. **Delivery**: Managed delivery via Resend API.
3. **Tracking**: Integrated delivery status tracking through Resend.

## Reference Materials
- [Delivery Policy](references/delivery-policy.md)
