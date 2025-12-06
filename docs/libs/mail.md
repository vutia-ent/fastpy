# Mail Facade

Send emails with multiple backend support.

## Supported Drivers

- `log` (default) - Logs to console (development)
- `smtp` - SMTP server
- `sendgrid` - SendGrid API
- `mailgun` - Mailgun API
- `ses` - AWS SES

## Basic Usage

```python
from fastpy_cli.libs import Mail

# Send with template
Mail.to('user@example.com') \
    .subject('Welcome!') \
    .send('welcome', {'name': 'John'})

# Send raw HTML
Mail.to('user@example.com') \
    .subject('Hello') \
    .html('<h1>Hello World</h1>') \
    .send()

# Send plain text
Mail.to('user@example.com') \
    .subject('Hello') \
    .text('Hello World') \
    .send()
```

## Recipients

```python
# Single recipient
Mail.to('user@example.com')

# Multiple recipients
Mail.to(['user1@example.com', 'user2@example.com'])

# CC
Mail.to('user@example.com') \
    .cc('manager@example.com')

# BCC
Mail.to('user@example.com') \
    .bcc('archive@example.com')

# All together
Mail.to('user@example.com') \
    .cc(['cc1@example.com', 'cc2@example.com']) \
    .bcc('archive@example.com') \
    .subject('Team Update') \
    .send('update', data)
```

## Sender

```python
# Set from address
Mail.to('user@example.com') \
    .from_address('noreply@myapp.com', 'My App') \
    .send('welcome')

# Set reply-to
Mail.to('user@example.com') \
    .reply_to('support@myapp.com') \
    .send('welcome')

# Set default from globally
Mail.set_default_from('noreply@myapp.com', 'My App')
```

## Templates

```python
# Use template with data
Mail.to('user@example.com') \
    .subject('Order Confirmation') \
    .send('orders/confirmation', {
        'order_id': 123,
        'items': items,
        'total': 99.99
    })

# Use view method (alias)
Mail.to('user@example.com') \
    .subject('Welcome') \
    .view('welcome', {'name': 'John'}) \
    .send()
```

## Attachments

```python
# Attach file
Mail.to('user@example.com') \
    .attach('/path/to/invoice.pdf') \
    .send('invoice')

# Attach with custom filename
Mail.to('user@example.com') \
    .attach('/path/to/file.pdf', filename='Invoice-123.pdf') \
    .send('invoice')

# Attach raw data
Mail.to('user@example.com') \
    .attach_data(pdf_bytes, 'invoice.pdf', 'application/pdf') \
    .send('invoice')
```

## Priority

```python
# High priority
Mail.to('user@example.com') \
    .high_priority() \
    .send('urgent')

# Low priority
Mail.to('user@example.com') \
    .low_priority() \
    .send('newsletter')

# Custom priority (1=high, 3=normal, 5=low)
Mail.to('user@example.com') \
    .priority(1) \
    .send('urgent')
```

## Custom Headers

```python
Mail.to('user@example.com') \
    .with_header('X-Custom', 'value') \
    .with_header('X-Campaign', 'welcome-2024') \
    .send('welcome')
```

## Queuing

```python
# Queue for later
Mail.to('user@example.com') \
    .queue('welcome', {'name': 'John'})

# Queue with delay (seconds)
Mail.to('user@example.com') \
    .later(60, 'reminder', {'name': 'John'})
```

## Using Specific Driver

```python
# Use SendGrid
Mail.using('sendgrid') \
    .to('user@example.com') \
    .send('welcome')

# Get driver instance
sendgrid = Mail.driver('sendgrid')
```

## Configuration

Set environment variables:

```bash
# SMTP
MAIL_DRIVER=smtp
MAIL_HOST=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=user
MAIL_PASSWORD=password
MAIL_ENCRYPTION=tls

# SendGrid
MAIL_DRIVER=sendgrid
SENDGRID_API_KEY=your-api-key

# Mailgun
MAIL_DRIVER=mailgun
MAILGUN_API_KEY=your-api-key
MAILGUN_DOMAIN=mg.example.com

# AWS SES
MAIL_DRIVER=ses
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
```

## Testing

```python
from fastpy_cli.libs import Mail

# Enable fake mode
Mail.fake()

# Send emails
Mail.to('user@example.com').subject('Test').send('welcome')

# Assertions
Mail.assert_sent('welcome')
Mail.assert_sent('welcome', count=1)
Mail.assert_not_sent('other_template')

# Access sent emails
for email in Mail.sent:
    print(email['to'], email['subject'])
```

## Complete Example

```python
from fastpy_cli.libs import Mail

class NotificationService:
    def send_welcome(self, user):
        Mail.to(user.email) \
            .subject('Welcome to Our App!') \
            .send('emails/welcome', {
                'name': user.name,
                'login_url': 'https://app.example.com/login'
            })

    def send_order_confirmation(self, order):
        Mail.to(order.user.email) \
            .cc(order.user.secondary_email) \
            .subject(f'Order #{order.id} Confirmed') \
            .attach_data(
                self.generate_invoice_pdf(order),
                f'invoice-{order.id}.pdf',
                'application/pdf'
            ) \
            .send('emails/order_confirmation', {
                'order': order,
                'items': order.items,
                'total': order.total
            })

    def send_password_reset(self, user, token):
        Mail.to(user.email) \
            .subject('Password Reset Request') \
            .high_priority() \
            .send('emails/password_reset', {
                'name': user.name,
                'reset_url': f'https://app.example.com/reset?token={token}'
            })
```
