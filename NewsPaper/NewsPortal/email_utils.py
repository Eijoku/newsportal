import logging
from typing import Iterable, Sequence

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_safe_mail(*, subject: str, message: str, recipients: Iterable[str]) -> None:
    """
    Safe mail sender used across the project.
    Skips sending when SMTP credentials are missing and logs failures.
    """
    emails: Sequence[str] = [email for email in recipients if email]
    if not emails:
        return
    if not getattr(settings, "EMAIL_HOST_USER", None):
        logger.warning("Skip email send: EMAIL_HOST_USER not configured")
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=list(emails),
            fail_silently=False,
        )
        logger.info("Email sent: %s -> %s", subject, emails)
    except Exception as exc:
        logger.error("Email send failed: %s", exc)
