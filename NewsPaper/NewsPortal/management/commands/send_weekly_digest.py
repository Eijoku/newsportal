from django.core.management.base import BaseCommand

from NewsPortal.tasks import send_weekly_digest


class Command(BaseCommand):
    help = "Send weekly digest of new articles to subscribed users"

    def handle(self, *args, **options):
        sent = send_weekly_digest()
        self.stdout.write(self.style.SUCCESS(f"Weekly digest sent: {sent} emails"))
