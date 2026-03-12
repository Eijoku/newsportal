from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

User = get_user_model()

@receiver(post_save, sender=User)
def add_user_to_common_on_create(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='common')
        instance.groups.add(group)

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