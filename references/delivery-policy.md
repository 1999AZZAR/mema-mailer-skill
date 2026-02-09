# Email Delivery Policy

## Provider
- **Service**: Resend (API-driven delivery)
- **Rate Limit**: Max 100 emails/day (Free Tier).
- **Domain**: Verified sender domain required via Resend dashboard.

## Security
- **API Key**: Managed via `RESEND_API_KEY` in `.env`.
- **Validation**: Strict input validation for recipient addresses.
- **Transport**: HTTPS (TLS 1.2+) enforced by Resend API.

## Templating (Jinja2)
- Templates stored in `assets/templates`.
- Dynamic content uses double curly braces `{{ }}`.
- Logic blocks use `{% %}`.

