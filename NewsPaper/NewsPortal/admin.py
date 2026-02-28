from django.contrib import admin
from .models import Author, Categories, Post, PostCategories, Comment

# ----------------------
# Author
# ----------------------
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating_author')  # колонки в списке
    search_fields = ('user__username',)

# ----------------------
# Categories
# ----------------------
@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name_categories',)
    search_fields = ('name_categories',)

# ----------------------
# Inline для PostCategories
# ----------------------
class PostCategoriesInline(admin.TabularInline):
    model = PostCategories
    extra = 1  # сколько пустых полей показывать

# ----------------------
# Actions для Post
# ----------------------
def make_like(modeladmin, request, queryset):
    for obj in queryset:
        obj.like()
make_like.short_description = "Поставить лайк"

def make_dislike(modeladmin, request, queryset):
    for obj in queryset:
        obj.dislike()
make_dislike.short_description = "Поставить дизлайк"

# ----------------------
# Post
# ----------------------
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'type_post', 'rating_post', 'time_create')
    list_filter = ('type_post', 'time_create', 'categories')
    search_fields = ('name', 'title', 'content')
    inlines = [PostCategoriesInline]
    actions = [make_like, make_dislike]

# ----------------------
# Actions для Comment
# ----------------------
def like_comment(modeladmin, request, queryset):
    for obj in queryset:
        obj.like()
like_comment.short_description = "Поставить лайк комментария"

def dislike_comment(modeladmin, request, queryset):
    for obj in queryset:
        obj.dislike()
dislike_comment.short_description = "Поставить дизлайк комментария"

# ----------------------
# Comment
# ----------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'rating_comment', 'time_create')
    list_filter = ('time_create', 'user')
    search_fields = ('text',)
    actions = [like_comment, dislike_comment]
