from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    AuthorDetailView,
    CategoryListView,
    posts_by_category,
    like_post,
    dislike_post,
    like_comment,
    dislike_comment
)

urlpatterns = [
    # Главная страница с постами
    path('news/', PostListView.as_view(), name='post_list'),

    # Детальная страница поста
    path('news/<int:pk>/', PostDetailView.as_view(), name='post_detail'),

    path('author/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),

    # Список категорий
    path('categories/', CategoryListView.as_view(), name='category_list'),

    # Посты по категории
    path('categories/<int:category_id>/', posts_by_category, name='posts_by_category'),

    # Лайки/дизлайки поста (AJAX)
    path('news/<int:pk>/like/', like_post, name='like_post'),
    path('news/<int:pk>/dislike/', dislike_post, name='dislike_post'),

    # Лайки/дизлайки комментариев (AJAX)
    path('comment/<int:pk>/like/', like_comment, name='like_comment'),
    path('comment/<int:pk>/dislike/', dislike_comment, name='dislike_comment'),
]