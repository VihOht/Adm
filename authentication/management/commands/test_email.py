from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Test email configuration by sending a test email"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to", type=str, help="Email address to send test email to", required=True
        )
        parser.add_argument(
            "--test-password-reset",
            action="store_true",
            help="Test password reset email for existing user",
        )

    def handle(self, *args, **options):
        to_email = options["to"]

        self.stdout.write("Testing email configuration...")
        self.stdout.write(f"Email Backend: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Email Host: {settings.EMAIL_HOST}")
        self.stdout.write(f"Email Port: {settings.EMAIL_PORT}")
        self.stdout.write(f"Use TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write("-" * 50)

        if options["test_password_reset"]:
            # Test password reset email
            try:
                user = User.objects.filter(email=to_email).first()
                if not user:
                    self.stdout.write(
                        self.style.ERROR(f"No user found with email: {to_email}")
                    )
                    return

                from django.contrib.auth.tokens import default_token_generator
                from django.template.loader import render_to_string
                from django.utils.encoding import force_bytes
                from django.utils.http import urlsafe_base64_encode

                # Generate token and uid
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Email context
                context = {
                    "email": user.email,
                    "domain": "localhost:8000",  # Change for production
                    "site_name": "VihOhtLife",
                    "uid": uid,
                    "user": user,
                    "token": token,
                    "protocol": "http",  # Change to 'https' for production
                }

                # Render email templates
                subject = render_to_string(
                    "registration/password_reset_subject.txt", context
                )
                subject = "".join(subject.splitlines())  # Remove newlines

                body = render_to_string(
                    "registration/password_reset_email.txt", context
                )

                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [to_email],
                    fail_silently=False,
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Password reset email sent successfully to {to_email}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to send password reset email: {str(e)}")
                )

        else:
            # Test basic email
            try:
                send_mail(
                    subject="VihOhtLife - Test Email",
                    message="This is a test email from VihOhtLife to verify email configuration.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[to_email],
                    fail_silently=False,
                )

                self.stdout.write(
                    self.style.SUCCESS(f"Test email sent successfully to {to_email}")
                )
                self.stdout.write(
                    "Please check the recipient's inbox (and spam folder)."
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to send test email: {str(e)}")
                )
                self.stdout.write("\nCommon solutions:")
                self.stdout.write(
                    "1. Check your email credentials in environment variables"
                )
                self.stdout.write(
                    "2. For Gmail: Use App Password, not regular password"
                )
                self.stdout.write("3. Verify 2-Factor Authentication is enabled")
                self.stdout.write("4. Check firewall/network settings")
                self.stdout.write("5. Verify EMAIL_HOST and EMAIL_PORT settings")

        self.stdout.write("-" * 50)
        self.stdout.write("Email configuration test completed.")
