from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import timezone
import logging

from .models import CategorySubscription, Post

logger = logging.getLogger(__name__)

User = get_user_model()


def send_safe_mail(*, subject: str, message: str, recipients):
    """Отправка почты с проверкой наличия SMTP-учётки и логированием ошибок."""
    if not recipients:
        return
    if not getattr(settings, 'EMAIL_HOST_USER', None):
        logger.warning("Skip email send: EMAIL_HOST_USER not configured")
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=list(recipients),
            fail_silently=False,
        )
        logger.info("Email sent: %s -> %s", subject, recipients)
    except Exception as exc:
        logger.error("Email send failed: %s", exc)


@receiver(post_save, sender=User)
def add_user_to_common_on_create(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(group)
        # приветственное письмо
        if instance.email:
            send_safe_mail(
                subject='Добро пожаловать!',
                message='Спасибо за регистрацию в NewsPortal. Вы можете подписываться на категории и получать уведомления о новых статьях.',
                recipients=[instance.email],
            )

@receiver(user_signed_up)
def allauth_user_signed_up(request, user, sociallogin=None, **kwargs):
    # 1) всегда добавляем в common
    group, _ = Group.objects.get_or_create(name='common')
    user.groups.add(group)

    # 2) если пришёл через соцсеть — попробуем взять email из extra_data
    if sociallogin:
        extra = getattr(sociallogin.account, 'extra_data', {}) or {}
        # Yandex может отдавать разные ключи; попробуем несколько вариантов
        email = extra.get('default_email') or extra.get('email') or extra.get('emails')
        if email and not user.email:
            user.email = email
            user.save()


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers_on_new_article(sender, instance: Post, action, pk_set, **kwargs):
    """Отправляем уведомление после привязки категорий к новой статье."""
    if action != 'post_add' or instance.type_post != 'articles':
        return

    # соберём подписчиков только по добавленным категориям
    subscribers = CategorySubscription.objects.filter(category_id__in=pk_set)
    emails = {sub.user.email for sub in subscribers if sub.user.email}
    if not emails:
        return

    site = Site.objects.get_current()
    link = f"https://{site.domain}/news/{instance.pk}/"
    preview = instance.preview()

    send_safe_mail(
        subject=f'Новая статья в ваших категориях: {instance.name}',
        message=f"{preview}\n\nЧитать полностью: {link}",
        recipients=list(emails),
    )
