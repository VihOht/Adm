# 📧 Email Configuration Guide for VihOhtLife

This guide will help you set up email functionality for password recovery and notifications in production.

## 🚀 Quick Start

### 1. Choose Your Email Provider

**For Personal/Small Projects:** Gmail (Free)
**For Production Applications:** SendGrid or Mailgun (Reliable, better deliverability)

### 2. Set Environment Variables

Copy `.env.example` to `.env` and configure your chosen provider:

```bash
cp .env.example .env
```

## 📋 Provider Setup Instructions

### 🔵 Gmail Setup (Recommended for Development/Personal Use)

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Factor Authentication

2. **Generate App Password**
   - Go to [App Passwords](https://support.google.com/accounts/answer/185833)
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Configure Environment Variables**
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-character-app-password
   DEFAULT_FROM_EMAIL=VihOhtLife <your-email@gmail.com>
   ```

### 🟢 SendGrid Setup (Recommended for Production)

1. **Create Account**
   - Sign up at [SendGrid](https://sendgrid.com/)
   - Verify your email

2. **Create API Key**
   - Go to Settings > API Keys
   - Create new API key with "Mail Send" permissions
   - Copy the API key

3. **Verify Sender**
   - Go to Settings > Sender Authentication
   - Verify your email or domain

4. **Configure Environment Variables**
   ```env
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your-sendgrid-api-key
   DEFAULT_FROM_EMAIL=VihOhtLife <noreply@yourdomain.com>
   ```

### 🟠 Mailgun Setup (Alternative Production Option)

1. **Create Account**
   - Sign up at [Mailgun](https://mailgun.com/)
   - Add and verify your domain

2. **Get SMTP Credentials**
   - Go to Sending > Domain settings
   - Find SMTP credentials

3. **Configure Environment Variables**
   ```env
   EMAIL_HOST=smtp.mailgun.org
   EMAIL_HOST_USER=postmaster@yourdomain.com
   EMAIL_HOST_PASSWORD=your-mailgun-smtp-password
   DEFAULT_FROM_EMAIL=VihOhtLife <noreply@yourdomain.com>
   ```

## 🔧 Railway Deployment Setup

### 1. Set Environment Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add these variables:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=VihOhtLife <your-email@gmail.com>
```

### 2. Update ALLOWED_HOSTS (if needed)

Make sure your domain is in `ALLOWED_HOSTS` in settings.py:

```python
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "vihohtlife.up.railway.app",
    "*.up.railway.app",
    "yourdomain.com",  # Add your custom domain
]
```

## 🧪 Testing Email Configuration

### 1. Test in Django Shell

```python
from django.core.mail import send_mail
from django.conf import settings

# Test basic email sending
send_mail(
    'Test Email',
    'This is a test email from VihOhtLife.',
    settings.DEFAULT_FROM_EMAIL,
    ['test@example.com'],
    fail_silently=False,
)
```

### 2. Test Password Recovery

1. Go to your login page
2. Click "Esqueceu sua senha?"
3. Enter a valid email address
4. Check if email is received

### 3. Check Logs

In production, check Railway logs for email-related errors:

```bash
railway logs
```

## 🔒 Security Best Practices

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique passwords
- Rotate API keys regularly

### 2. Email Security
- Use App Passwords for Gmail (not regular passwords)
- Enable 2FA on all email provider accounts
- Use HTTPS for all email-related pages

### 3. Production Settings
- Set `DEBUG=false` in production
- Use secure cookies (`SESSION_COOKIE_SECURE=True`)
- Enable HSTS headers

## 🚨 Troubleshooting

### Common Issues

1. **"SMTPAuthenticationError"**
   - Check username/password
   - For Gmail: Use App Password, not regular password
   - Verify 2FA is enabled

2. **"SMTPConnectTimeoutError"**
   - Check EMAIL_HOST and EMAIL_PORT
   - Verify firewall/network settings

3. **"Email not received"**
   - Check spam folder
   - Verify sender email is authenticated
   - Check email provider logs

4. **"CSRF Verification Failed"**
   - Add your domain to `CSRF_TRUSTED_ORIGINS`
   - Ensure HTTPS is properly configured

### Debug Commands

```bash
# Test email configuration
python manage.py shell
>>> from django.core.mail import send_test_mail
>>> send_test_mail(['admin@example.com'])

# Check email backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_BACKEND)
>>> print(settings.EMAIL_HOST)
```

## 📊 Monitoring & Analytics

### Email Delivery Monitoring

1. **SendGrid:** Built-in analytics dashboard
2. **Mailgun:** Detailed delivery reports
3. **Gmail:** Basic sending history

### Django Logging

Add email logging to settings.py:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
```

## 🎯 Email Templates

The password recovery emails use these templates:
- `templates/registration/password_reset_email.txt`
- `templates/registration/password_reset_subject.txt`

Customize them to match your brand:

```html
<!-- password_reset_email.txt -->
Olá {{ user.get_full_name|default:user.username }},

Você solicitou a redefinição de sua senha para o VihOhtLife.

Clique no link abaixo para criar uma nova senha:
{{ protocol }}://{{ domain }}{% url 'authentication:password_reset_confirm' uidb64=uid token=token %}

Este link expira em 3 dias.

Se você não solicitou esta redefinição, ignore este email.

Atenciosamente,
Equipe VihOhtLife
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Railway deployment logs
3. Verify email provider status pages
4. Test with a simple email send script

---

**Note:** Always test email functionality in a staging environment before deploying to production!
