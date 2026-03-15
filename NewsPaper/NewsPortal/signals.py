from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

from .email_utils import send_safe_mail
from .models import Post
from .tasks import send_new_post_notification

User = get_user_model()


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

    send_new_post_notification.delay(instance.pk, list(pk_set))
