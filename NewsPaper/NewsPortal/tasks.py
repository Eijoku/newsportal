from datetime import timedelta
from typing import Iterable, List, Sequence

from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.sites.models import Site
from django.utils import timezone

from .email_utils import send_safe_mail
from .models import CategorySubscription, Post

logger = get_task_logger(__name__)


def _collect_subscriber_emails(category_ids: Iterable[int]) -> Sequence[str]:
    """Return unique emails of users subscribed to given categories."""
    subs = CategorySubscription.objects.filter(category_id__in=category_ids).select_related("user")
    return {sub.user.email for sub in subs if sub.user.email}


@shared_task
def send_new_post_notification(post_id: int, category_ids: List[int] | None = None) -> int:
    """
    Рассылка по подпискам после создания статьи.
    Возвращает количество адресатов.
    """
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        logger.warning("Post %s not found for notification", post_id)
        return 0

    categories = category_ids or list(post.categories.values_list("id", flat=True))
    emails = _collect_subscriber_emails(categories)
    if not emails:
        return 0

    site = Site.objects.get_current()
    link = f"https://{site.domain}/news/{post.pk}/"
    preview = post.preview()

    send_safe_mail(
        subject=f"Новая статья в ваших категориях: {post.name}",
        message=f"{preview}\n\nЧитать полностью: {link}",
        recipients=list(emails),
    )
    logger.info("Post %s notification sent to %s users", post_id, len(emails))
    return len(emails)


@shared_task
def send_weekly_digest() -> int:
    """
    Еженедельная рассылка: последние статьи по подпискам за 7 дней.
    Возвращает количество отправленных писем.
    """
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    site = Site.objects.get_current()

    # Предкешируем посты по категориям
    posts = Post.objects.filter(type_post="articles", time_create__gte=week_ago).prefetch_related("categories")
    posts_by_category: dict[int, list[Post]] = {}
    for post in posts:
        for cat in post.categories.all():
            posts_by_category.setdefault(cat.id, []).append(post)

    sent = 0
    for sub in CategorySubscription.objects.select_related("user", "category"):
        user_email = sub.user.email
        if not user_email:
            continue

        cat_posts = posts_by_category.get(sub.category_id, [])
        if not cat_posts:
            continue

        lines = [f"• {p.name} — https://{site.domain}/news/{p.pk}/" for p in cat_posts]
        body = (
            f"Новые статьи в категории {sub.category.name_categories} за неделю:\n"
            + "\n".join(lines)
        )

        send_safe_mail(
            subject=f"Дайджест: {sub.category.name_categories}",
            message=body,
            recipients=[user_email],
        )
        sent += 1

    logger.info("Weekly digest sent to %s users", sent)
    return sent
