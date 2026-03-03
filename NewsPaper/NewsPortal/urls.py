# NewsPortal/urls.py
from django.urls import path
from .views import (
    PostSearchView,
    PostListView,
    PostDetailView,
    AuthorDetailView,
    CategoryListView,
    posts_by_category,
    like_post,
    dislike_post,
    like_comment,
    dislike_comment,
    NewsCreateView, 
    ArticleCreateView,
    PostUpdateView, 
    PostDeleteView
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
    
    path('news/search/', PostSearchView.as_view(), name='post_search'),
    
    # --- Новости ---
    path('news/create/', NewsCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', PostUpdateView.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', PostDeleteView.as_view(), name='news_delete'),

    # --- Статьи ---
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', PostUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', PostDeleteView.as_view(), name='article_delete'),
]