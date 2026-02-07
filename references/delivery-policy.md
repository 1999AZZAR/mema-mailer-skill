# Email Delivery Policy

## Provider
- **Service**: Resend.com
- **Rate Limit**: Max 100 emails/day (Free Tier).
- **Domain**: Must be verified in Resend dashboard.

## Security
- **API Key**: `re_***` (Never commit this!)
- **SPF/DKIM**: Ensure DNS records are valid to avoid spam folder.

## Templating (Jinja2)
- All templates extend `base.html`.
- Use `{{ variable }}` for dynamic content.
- Use `{% block content %}` for unique body content.
