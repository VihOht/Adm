"""
Management command to test email configuration and password reset functionality.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class Command(BaseCommand):
    help = "Test email configuration and password reset functionality"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            type=str,
            required=True,
            help="Email address to send test email to",
        )
        parser.add_argument(
            "--test-password-reset",
            action="store_true",
            help="Test password reset email specifically",
        )
        parser.add_argument(
            "--check-config",
            action="store_true",
            help="Check email configuration only",
        )

    def handle(self, *args, **options):
        email_to = options["to"]
        test_password_reset = options.get("test_password_reset", False)
        check_config = options.get("check_config", False)

        if check_config:
            self.check_email_configuration()
            return

        if test_password_reset:
            self.test_password_reset_email(email_to)
        else:
            self.test_basic_email(email_to)

    def check_email_configuration(self):
        """Check if email is properly configured"""
        self.stdout.write("🔍 Checking email configuration...")

        # Check required settings
        config_issues = []

        if not hasattr(settings, "EMAIL_BACKEND"):
            config_issues.append("EMAIL_BACKEND not set")
        else:
            self.stdout.write(f"✅ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

        if not hasattr(settings, "EMAIL_HOST") or not settings.EMAIL_HOST:
            config_issues.append("EMAIL_HOST not set")
        else:
            self.stdout.write(f"✅ EMAIL_HOST: {settings.EMAIL_HOST}")

        if not hasattr(settings, "EMAIL_HOST_USER") or not settings.EMAIL_HOST_USER:
            config_issues.append("EMAIL_HOST_USER not set")
        else:
            self.stdout.write(f"✅ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

        if (
            not hasattr(settings, "EMAIL_HOST_PASSWORD")
            or not settings.EMAIL_HOST_PASSWORD
        ):
            config_issues.append("EMAIL_HOST_PASSWORD not set")
        else:
            self.stdout.write("✅ EMAIL_HOST_PASSWORD: [CONFIGURED]")

        if (
            not hasattr(settings, "DEFAULT_FROM_EMAIL")
            or not settings.DEFAULT_FROM_EMAIL
        ):
            config_issues.append("DEFAULT_FROM_EMAIL not set")
        else:
            self.stdout.write(f"✅ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

        # Additional settings
        self.stdout.write(
            f"📧 EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}"
        )
        self.stdout.write(
            f"🔐 EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}"
        )
        self.stdout.write(
            f"🔒 EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'Not set')}"
        )

        if config_issues:
            self.stdout.write(self.style.ERROR("❌ Configuration issues found:"))
            for issue in config_issues:
                self.stdout.write(f"   - {issue}")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Email configuration looks good!"))

    def test_basic_email(self, email_to):
        """Test basic email sending"""
        self.stdout.write(f"📧 Testing basic email to: {email_to}")

        try:
            subject = "VihOhtLife - Test Email"
            message = """
            Olá!
            
            Este é um email de teste do sistema VihOhtLife.
            
            Se você recebeu este email, significa que a configuração de email está funcionando corretamente.
            
            Atenciosamente,
            Equipe VihOhtLife
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email_to],
                fail_silently=False,
            )

            self.stdout.write(self.style.SUCCESS("✅ Test email sent successfully!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send test email: {e}"))
            raise CommandError(f"Email test failed: {e}")

    def test_password_reset_email(self, email_to):
        """Test password reset email"""
        self.stdout.write(f"🔑 Testing password reset email to: {email_to}")

        try:
            # Try to find user by email, create temp user if not found
            try:
                user = User.objects.get(email=email_to)
                self.stdout.write(f"📝 Using existing user: {user.username}")
            except User.DoesNotExist:
                # Create temporary user for testing
                import uuid

                temp_username = f"temp_test_{uuid.uuid4().hex[:8]}"
                user = User.objects.create_user(
                    username=temp_username, email=email_to, password="temp_password_123"
                )
                self.stdout.write(f"📝 Created temporary user: {user.username}")
                self.stdout.write("⚠️  Remember to delete this user after testing")

            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Create reset link (using localhost for testing)
            reset_link = f"http://localhost:8000{reverse('authentication:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"

            # Email context
            context = {
                "email": user.email,
                "domain": "localhost:8000",
                "site_name": "VihOhtLife",
                "uid": uid,
                "user": user,
                "token": token,
                "protocol": "http",
                "reset_url": reset_link,
            }

            # Check if templates exist
            try:
                subject = render_to_string(
                    "registration/password_reset_subject.txt", context
                )
                subject = "".join(subject.splitlines())

                body = render_to_string(
                    "registration/password_reset_email.txt", context
                )

                self.stdout.write("✅ Email templates rendered successfully")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Template rendering failed: {e}")
                )
                raise CommandError(f"Template error: {e}")

            # Send email
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [email_to],
                fail_silently=False,
            )

            self.stdout.write(
                self.style.SUCCESS("✅ Password reset email sent successfully!")
            )
            self.stdout.write(f"🔗 Reset link: {reset_link}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to send password reset email: {e}")
            )
            raise CommandError(f"Password reset email test failed: {e}")
