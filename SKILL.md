---
name: mema-mailer
description: Professional email delivery system using msmtp and Python-based HTML templating (Jinja2). Use when user asks to "send email", "notify me", "send report".
---

# Mema Mailer

## Setup
1.  Copy `.env.example` to `.env`.
2.  Set `RESEND_API_KEY` (from Resend.com).
3.  Ensure Python dependencies (`jinja2`, `requests`) are installed.

## Usage
- **Role**: Executive Assistant.
- **Trigger**: "Email me this", "Send daily report".
- **Output**: Sent email status + preview link (if available).

## Capabilities
1.  **Templating**: Beautiful HTML emails (`assets/templates`).
2.  **Delivery**: Reliable sending via Resend API.
3.  **Logs**: Track sent emails (status, timestamp).

## Reference Materials
- [Delivery Policy](references/delivery-policy.md)
