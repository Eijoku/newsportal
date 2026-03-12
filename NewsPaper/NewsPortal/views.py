# NewsPortal/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Categories, Comment, Author, CategorySubscription
from django.db.models import Count
from .forms import PostForm
from django.http import JsonResponse
from .filters import PostFilter
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

# Список постов
class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    ordering = ['-time_create']
    paginate_by = 10

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
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = CategorySubscription.objects.filter(category=category, user=request.user).exists()
    return render(request, 'posts_by_category.html', {
        'category': category,
        'posts': posts,
        'is_subscribed': is_subscribed,
    })


@login_required
@require_POST
def subscribe_category(request, category_id):
    category = get_object_or_404(Categories, id=category_id)
    CategorySubscription.objects.get_or_create(category=category, user=request.user)
    messages.success(request, f'Вы подписались на категорию {category.name_categories}.')
    return redirect('posts_by_category', category_id=category_id)


@login_required
@require_POST
def unsubscribe_category(request, category_id):
    category = get_object_or_404(Categories, id=category_id)
    CategorySubscription.objects.filter(category=category, user=request.user).delete()
    messages.success(request, f'Подписка на категорию {category.name_categories} отменена.')
    return redirect('posts_by_category', category_id=category_id)

def like_post(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            from django.urls import reverse
            return JsonResponse({'redirect': reverse('account_login')}, status=403)
        post = get_object_or_404(Post, pk=pk)
        from .models import PostVote
        pv, created = PostVote.objects.get_or_create(post=post, user=request.user, defaults={'vote': 1})
        if created:
            # новый лайк поставлен
            pass
        else:
            # повторный клик по лайку снимает его
            if pv.vote == 1:
                pv.delete()
            else:
                pv.vote = 1
                pv.save()
        # recompute rating
        likes = PostVote.objects.filter(post=post, vote=1).count()
        dislikes = PostVote.objects.filter(post=post, vote=-1).count()
        post.rating_post = likes - dislikes
        post.save()
        post.author.update_rating()
        return JsonResponse({"rating": post.rating_post})

def dislike_post(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            from django.urls import reverse
            return JsonResponse({'redirect': reverse('account_login')}, status=403)
        post = get_object_or_404(Post, pk=pk)
        from .models import PostVote
        pv, created = PostVote.objects.get_or_create(post=post, user=request.user, defaults={'vote': -1})
        if created:
            # новый дизлайк поставлен
            pass
        else:
            # повторный клик по дизлайку снимает его
            if pv.vote == -1:
                pv.delete()
            else:
                pv.vote = -1
                pv.save()
        # recompute rating
        likes = PostVote.objects.filter(post=post, vote=1).count()
        dislikes = PostVote.objects.filter(post=post, vote=-1).count()
        post.rating_post = likes - dislikes
        post.save()
        post.author.update_rating()
        return JsonResponse({"rating": post.rating_post})


def like_comment(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            from django.urls import reverse
            return JsonResponse({'redirect': reverse('account_login')}, status=403)
        comment = get_object_or_404(Comment, pk=pk)
        from .models import CommentVote
        cv, created = CommentVote.objects.get_or_create(comment=comment, user=request.user, defaults={'vote': 1})
        if created:
            pass
        else:
            if cv.vote == 1:
                cv.delete()
            else:
                cv.vote = 1
                cv.save()
        likes = CommentVote.objects.filter(comment=comment, vote=1).count()
        dislikes = CommentVote.objects.filter(comment=comment, vote=-1).count()
        comment.rating_comment = likes - dislikes
        comment.save()
        comment.post.author.update_rating()
        return JsonResponse({"rating": comment.rating_comment})


def dislike_comment(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            from django.urls import reverse
            return JsonResponse({'redirect': reverse('account_login')}, status=403)
        comment = get_object_or_404(Comment, pk=pk)
        from .models import CommentVote
        cv, created = CommentVote.objects.get_or_create(comment=comment, user=request.user, defaults={'vote': -1})
        if created:
            pass
        else:
            if cv.vote == -1:
                cv.delete()
            else:
                cv.vote = -1
                cv.save()
        likes = CommentVote.objects.filter(comment=comment, vote=1).count()
        dislikes = CommentVote.objects.filter(comment=comment, vote=-1).count()
        comment.rating_comment = likes - dislikes
        comment.save()
        comment.post.author.update_rating()
        return JsonResponse({"rating": comment.rating_comment})

@login_required
def become_author(request):
    if request.method == 'POST' or request.method == 'GET':
        authors, _ = Group.objects.get_or_create(name='authors')
        request.user.groups.add(authors)
        # ensure Author object exists for this user
        from .models import Author
        Author.objects.get_or_create(user=request.user)
    return redirect('post_list')

class PostSearchView(ListView):
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'posts'  # используем posts для совместимости

    def get_queryset(self):
        # Создаём фильтр с GET-параметрами
        self.filter = PostFilter(self.request.GET, queryset=Post.objects.all().order_by('-time_create'))
        return self.filter.qs  # возвращаем отфильтрованные объекты

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter  # передаём фильтр в шаблон
        return context
    

# --- Создание новости ---
class NewsCreateView(UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'  # используем один шаблон
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = 'news'  # правильное имя поля
        from .models import Author
        author_obj, _ = Author.objects.get_or_create(user=self.request.user)
        post.author = author_obj  # присваиваем автора
        post.save()
        form.save_m2m()
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='authors').exists()

# --- Создание статьи ---
class ArticleCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = 'articles'  # правильное имя поля
        from .models import Author
        author_obj, _ = Author.objects.get_or_create(user=self.request.user)
        post.author = author_obj
        post.save()
        form.save_m2m()
        return super().form_valid(form)

# --- Редактирование ---
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')

# --- Удаление ---
class PostDeleteView(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    login_url = '/accounts/login/'
    # остальная реализация

@login_required
def become_author(request):
    # Если хотите разрешать GET, уберите проверку на метод
    if request.method == 'POST' or request.method == 'GET':
        authors, _ = Group.objects.get_or_create(name='authors')
        request.user.groups.add(authors)
    return redirect('post_list')


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    text = request.POST.get('text', '').strip()
    if text:
        Comment.objects.create(post=post, user=request.user, text=text)
    return redirect('post_detail', pk=pk)


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user == request.user:
        post_pk = comment.post.pk
        comment.delete()
        return redirect('post_detail', pk=post_pk)
    return redirect('post_list')
