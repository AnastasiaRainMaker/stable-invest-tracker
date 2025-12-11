from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Sends a test email to verify SMTP configuration'

    def handle(self, *args, **options):
        self.stdout.write("Attempting to send test email...")
        self.stdout.write(f"From: {settings.ALERT_FROM_EMAIL}")
        self.stdout.write(f"To: {settings.ALERT_RECIPIENT_EMAIL}")
        
        if not settings.EMAIL_HOST_PASSWORD:
            self.stdout.write(self.style.ERROR("Error: EMAIL_HOST_PASSWORD environment variable is not set."))
            self.stdout.write("Please run: export EMAIL_HOST_PASSWORD='your-app-password' && python manage.py send_test_email")
            return

        try:
            send_mail(
                subject='StableInvest Test Email',
                message='This is a test email from your StableInvest Tracker app. If you see this, real email sending is working!',
                from_email=settings.ALERT_FROM_EMAIL,
                recipient_list=[settings.ALERT_RECIPIENT_EMAIL],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Email sent! Check your inbox.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))
