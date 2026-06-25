---
name: mema-mailer
description: Professional email delivery system using the Resend API and Jinja2 HTML templating with Swiss-Archival design. Use when user asks to "send email", "notify me", "send report", "send invoice", "send newsletter", "email alert".
---

# Mema Mailer

AI-powered email delivery system with Swiss-Archival designed templates, Resend API integration, and Jinja2 templating.

## Quick Start

```bash
# 1. Setup
cp .env.example .env
# Edit .env with your RESEND_API_KEY

# 2. Install deps
pip install jinja2 requests python-dotenv

# 3. Send email
python3 scripts/mailer.py \
  --to "user@example.com" \
  --subject "Hello" \
  --template default \
  --context '{"name": "Azzar", "message": "Hello world"}'
```

## CLI Arguments

| Arg | Required | Description |
|---|---|---|
| `--to` | Yes* | Comma-separated recipient emails |
| `--subject` | Yes* | Email subject line |
| `--template` | No | Template name without `.html` (default: `default`) |
| `--context` | No | JSON string of template variables |
| `--context-file` | No | Path to JSON file with template variables |
| `--cc` | No | Comma-separated CC emails |
| `--bcc` | No | Comma-separated BCC emails |
| `--reply-to` | No | Reply-To address |
| `--dry-run` | No | Render template only, do not send |
| `--batch` | No | Comma-separated recipients for individual sends |
| `--list-templates` | No | List all available templates and exit |
| `--api-key` | No | Resend API key (overrides env) |
| `--sender` | No | Sender email (overrides env) |
| `-v, --verbose` | No | Verbose/debug output |

*Required unless `--batch` or `--list-templates` is used.

## Template Map

### Core Templates

| Template | Use Case | Types/Variants |
|---|---|---|
| `base` | Foundation layout (extended by others) | N/A - do not use directly |
| `default` | Simple one-off messages | `name`, `message`, `action_url`, `action_text` |
| `basic` | Minimal no-frills message | `title`, `message`, `action_url` |
| `message` | Direct multi-paragraph message | `title`, `paragraphs[]`, `action.url`, `action.text` |

### Alert Templates

| Template | Use Case | Types/Variants |
|---|---|---|
| `alert` | System alerts, warnings, errors | `severity`: critical, warning, info, success |

**Variables:**
```
severity: critical | warning | info | success
alert_title: string
alert_message: string
title: string
description: string
affected_items: string[]
details: {key: value}
metrics: [{name, value, status, status_label}]
action_url: string
action_text: string
timestamp: string
```

### Business Templates

| Template | Use Case | Types/Variants |
|---|---|---|
| `business` | Business communications | `type`: invoice, proposal, receipt, (default) update |

**Invoice Variables:**
```
type: invoice
invoice_number: INV-0001
client_name: string
client_email: string
issue_date: string
due_date: string
items: [{description, amount}]
total: $0.00
payment_url: string
payment_text: Pay Now
```

**Proposal Variables:**
```
type: proposal
title: Project Proposal
summary: string
sections: [{title, content, items[]}]
pricing: [{name, price, period, features[], featured}]
action_url: string
action_text: Accept Proposal
```

**Receipt Variables:**
```
type: receipt
total: $0.00
reference: REF-0001
date: string
payment_method: string
items: [{name, amount}]
```

**Default Update Variables:**
```
title: Business Update
message: string
highlights: string[]
metrics: [{value, label}]
action_url: string
action_text: View Details
signature: {name, title, email}
```

### Personal Templates

| Template | Use Case | Types/Variants |
|---|---|---|
| `personal` | Personal, casual, fun messages | `type`: greeting, invitation, note, congrats, reminder, recommendation |

**Greeting Variables:**
```
type: greeting
icon: emoji
title: Hello!
message: string
signature: string
```

**Invitation Variables:**
```
type: invitation
event_image: URL
title: Event Name
event_date: string
event_time: string
event_location: string
description: string
action_url: string
action_text: RSVP
```

**Note Variables:**
```
type: note
from_name: string
message: string
action_url: string
action_text: Reply
```

**Congrats Variables:**
```
type: congrats
message: string
achievement: string
```

**Reminder Variables:**
```
type: reminder
title: string
message: string
event_date: string
event_time: string
event_location: string
action_url: string
```

**Recommendation Variables:**
```
type: recommendation
title: string
media_image: URL
message: string
rating: string
action_url: string
action_text: Learn More
```

**Common:** `ps` (postscript text)

### Inquiry Templates

| Template | Use Case | Types/Variants |
|---|---|---|
| `inquiry` | Questions, support, feedback | `type`: support, feedback, question, survey |

**Support Variables:**
```
type: support
ticket_id: TKT-0001
priority: low | medium | high | critical
category: string
message: string
steps: string[]
action_url: string
action_text: View Ticket
```

**Feedback Variables:**
```
type: feedback
title: string
questions: [{text, type: rating | yes_no}]
response_url: string
response_text: Submit Feedback
```

**Question Variables:**
```
type: question
from_name: string
from_email: string
subject: string
message: string
context: {key: value}
reply_url: string
reply_text: Reply
```

**Survey Variables:**
```
type: survey
title: string
description: string
questions: [{text, type: multiple_choice | text, options[]}]
submit_url: string
submit_text: Submit Survey
```

### Newsletter Templates

| Template | Use Case | Types/Variants |
|---|---|---|
| `newsletter` | Newsletters, digests, announcements | `type`: announcement, digest, changelog, curated, report |

**Announcement Variables:**
```
type: announcement
title: string
date: string
hero_image: URL
content: HTML string
highlights: string[]
action_url: string
action_text: Learn More
```

**Digest Variables:**
```
type: digest
period: Weekly Digest
title: string
date_range: string
summary: string
sections: [{title, content, items[], link, link_text}]
stats: [{value, label}]
```

**Changelog Variables:**
```
type: changelog
title: What's New
version: string
changes: [{type: added | fixed | improved | removed, title, description, items[]}]
action_url: string
```

**Curated Variables:**
```
type: curated
title: string
items: [{image, category, title, description, url}]
```

**Report Variables:**
```
type: report
title: Monthly Report
period: string
metrics: [{value, label, trend: up | down}]
sections: [{title, content, table: {headers[], rows[]}}]
next_report: string
```

**Common:** `unsubscribe_url`

### System Report Templates

| Template | Use Case |
|---|---|
| `system_report` | Server health, diagnostics, monitoring |
| `skills_report` | Skills audit, capability report |
| `report` | Generic analytics, progress, data tables |
| `neo_hybrid_report` | Standalone branded report (does not extend base) |

**System Report Variables:**
```
title: System Health Dashboard
overall_status: healthy | degraded | critical
summary: [{value, label}]
oci: {title, uptime, load, mem, disk, docker, network}
pihole: {title, total_queries, ads_blocked, percent_blocked, top_clients, domains}
lappy: {title, status, uptime, load, mem, disk}
services: [{name, status: running | stopped | warning}]
custom_sections: [{title, color, data: {key: value}}]
alerts: [{severity, title, message}]
next_check: string
now: timestamp
```

### Other Templates

| Template | Use Case |
|---|---|
| `confirmation` | Action success/error, transactions |
| `professional` | Formal correspondence with key-value pairs |
| `welcome` | Onboarding, getting started |
| `notification` | General notifications with optional alert |

**Confirmation Variables:**
```
status: success | error
success_title: string
error_title: string
message: string
transaction_id: string
transaction_date: string
amount: string
items: [[cells]]
table_headers: [headers]
next_steps: string[]
action_url: string
secondary_url: string
support_info: string
```

**Professional Variables:**
```
title: string
name: string
message: string
items: {label: value}
action_url: string
action_text: string
```

**Welcome Variables:**
```
name: string
subtitle: string
welcome_message: string
features: [{title, description}]
quick_links: [{text, url}]
action_url: string
action_text: Get Started
```

## Design System: Swiss-Archival

All templates use the Swiss-Archival design language:

| Token | Value | Usage |
|---|---|---|
| Background | `#EFE9DC` | Canvas |
| Surface | `#EEE8DB` | Cards |
| Foreground | `#2A2520` | Text |
| Accent | `#9C3D3B` | Buttons, links, emphasis |
| Muted | `#CBC3B7` | Borders, dividers |
| Muted FG | `#6F675D` | Labels, metadata |
| Success | `#3A6B3A` | Positive states |
| Warning | `#8B6B1A` | Caution states |

**Fonts:** Plus Jakarta Sans (narrative), JetBrains Mono (metadata)
**Border Radius:** 4px
**Print:** `[ ARCHIVAL_PRINT_SPECIMEN ]` footer auto-added

## Architecture

```
mema-mailer/
├── SKILL.md                    # This file
├── .env.example                # Config template
├── scripts/
│   └── mailer.py               # CLI + MemaMailer class
├── assets/
│   └── templates/
│       ├── base.html           # Foundation (all others extend this)
│       ├── alert.html          # Alerts & warnings
│       ├── business.html       # Invoices, proposals, receipts
│       ├── personal.html       # Greetings, invitations, notes
│       ├── inquiry.html        # Support, feedback, surveys
│       ├── newsletter.html     # Announcements, digests
│       ├── system_report.html  # Server diagnostics
│       ├── confirmation.html   # Success/error states
│       ├── professional.html   # Formal correspondence
│       ├── report.html         # Analytics & data tables
│       ├── welcome.html        # Onboarding
│       └── ...                 # Additional templates
└── references/
    └── delivery-policy.md      # Delivery rules
```

## Programmatic Usage

```python
from scripts.mailer import MemaMailer

mailer = MemaMailer()

result = mailer.send(
    to_emails=["user@example.com"],
    subject="Monthly Report",
    template_name="newsletter",
    context={
        "type": "report",
        "title": "June 2026 Report",
        "period": "June 1-30, 2026",
        "metrics": [
            {"value": "1,234", "label": "Users", "trend": "up"},
            {"value": "567", "label": "Orders", "trend": "up"}
        ]
    }
)

print(result)
# {"status": "success", "message": "Email sent to user@example.com", "resend_id": "..."}
```

## Template Inheritance

All templates extend `base.html` and can override:

```jinja2
{% block artifact_class %}ALERT{% endblock %}
{% block header_class %}header-accent{% endblock %}
{% block brand %}CUSTOM BRAND{% endblock %}
{% block brand_sub %}Custom subtitle{% endblock %}
{% block content %}...{% endblock %}
{% block footer %}...{% endblock %}
```

**Header variants:** `header` (default dark), `header-accent` (burgundy), `header-minimal` (light with border)

## Reference Materials

- [Delivery Policy](references/delivery-policy.md)
