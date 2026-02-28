from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Post, Categories, Comment, Author
from django.db.models import Count
from django.http import JsonResponse

# Список постов
class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    ordering = ['-time_create']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categories.objects.all()  # добавляем категории
        context['top_authors'] = Author.objects.order_by(
            '-rating_author'
        )[:5]
        return context
    
    def get_queryset(self):
        return Post.objects.annotate(num_comments=Count('comment')).order_by('-time_create')

# Детальная страница поста
class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categories.objects.all()
        context['comments'] = self.object.comment_set.all()  # все комментарии поста
        return context

# Список категорий
class CategoryListView(ListView):
    model = Categories
    template_name = 'category_list.html'
    context_object_name = 'categories'

class AuthorDetailView(ListView):
    model = Post
    template_name = 'author_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.author = Author.objects.get(pk=self.kwargs['pk'])
        return Post.objects.filter(author=self.author).order_by('-time_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['categories'] = Categories.objects.all()
        return context

# Посты по категории
def posts_by_category(request, category_id):
    category = get_object_or_404(Categories, id=category_id)
    posts = Post.objects.filter(categories=category).order_by('-time_create')
    return render(request, 'posts_by_category.html', {'category': category, 'posts': posts})

def like_post(request, pk):
    if request.method == "POST":
        post = Post.objects.get(pk=pk)
        post.like()
        return JsonResponse({"rating": post.rating_post})

def dislike_post(request, pk):
    if request.method == "POST":
        post = Post.objects.get(pk=pk)
        post.dislike()
        return JsonResponse({"rating": post.rating_post})


def like_comment(request, pk):
    if request.method == "POST":
        comment = Comment.objects.get(pk=pk)
        comment.like()
        return JsonResponse({"rating": comment.rating_comment})


def dislike_comment(request, pk):
    if request.method == "POST":
        comment = Comment.objects.get(pk=pk)
        comment.dislike()
        return JsonResponse({"rating": comment.rating_comment})