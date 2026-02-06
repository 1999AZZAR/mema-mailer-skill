---
name: mema-mailer
description: Professional email delivery system using msmtp and Python-based HTML templating.
---

# Mema Mailer Skill

A lightweight, robust email delivery system for Mema to communicate via domain-branded emails.

## Core Capabilities

### 1. SMTP & API Delivery
Professional mail delivery using Resend API (default) or msmtp.
- **Engine:** Resend API for clean domain-branded sending.
- **Sender:** `mema@glassgallery.my.id`.

### 2. HTML Templating (Jinja2)
Design and send beautiful, responsive emails.
- **Templates:** Stored in `templates/` folder.
- **Dynamic Content:** Inject variables into HTML designs.

### 3. CLI Integration
Send emails directly from the workspace.
- **Usage:** `python3 scripts/mema_mail_resend.py --to "user@email.com" --subject "Hello" --template "default"`

## Folder Structure
- `scripts/`: Python orchestration for sending and templating.
- `templates/`: HTML/CSS designs for different types of emails.
- `.env`: (Ignored) SMTP credentials.

## Workflow
1. **Prepare Template:** Edit HTML files in `templates/`.
2. **Execute:** Run the mailer script with desired parameters.
3. **Verify:** Check destination inbox (forwarding ensures Azzar sees everything).
