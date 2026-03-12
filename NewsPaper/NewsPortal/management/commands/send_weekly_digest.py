from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings

from NewsPortal.models import CategorySubscription, Post


class Command(BaseCommand):
    help = "Send weekly digest of new articles to subscribed users"

    def handle(self, *args, **options):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        site = Site.objects.get_current()

        # Сгруппируем посты по подпискам пользователя
        subscriptions = CategorySubscription.objects.select_related('user', 'category')
        posts = Post.objects.filter(type_post='articles', time_create__gte=week_ago)

        # Предкешируем посты по категории
        posts_by_category = {}
        for post in posts.prefetch_related('categories'):
            for cat in post.categories.all():
                posts_by_category.setdefault(cat.id, []).append(post)

        sent = 0
        for sub in subscriptions:
            user_email = sub.user.email
            if not user_email:
                continue

            cat_posts = posts_by_category.get(sub.category_id, [])
            if not cat_posts:
                continue

            lines = [
                f"• {p.name} — https://{site.domain}/news/{p.pk}/"
                for p in cat_posts
            ]
            body = (
                f"Новые статьи в категории {sub.category.name_categories} за неделю:\n" +
                "\n".join(lines)
            )

            send_mail(
                subject=f"Дайджест: {sub.category.name_categories}",
                message=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                recipient_list=[user_email],
                fail_silently=True,
            )
            sent += 1

        self.stdout.write(self.style.SUCCESS(f"Weekly digest sent: {sent} emails"))
