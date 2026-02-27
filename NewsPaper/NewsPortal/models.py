from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum



class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating_author = models.IntegerField(default=0)

    def update_rating(self):
        total_post_rating = self.post_set.aggregate(total=Sum('rating_post'))['total'] or 0
        total_comments_on_posts = Comment.objects.filter(post__author=self).aggregate(total=Sum('rating_comment'))['total'] or 0
        self.rating_author = total_post_rating * 3 + total_comments_on_posts
        self.save()

class Categories(models.Model):
    name_categories = models.CharField(max_length=255, unique=True)

POST_CHOICES = [
    ('articles', 'статья'),
    ('news', 'новость'),
]

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type_post = models.CharField(max_length=20, choices=POST_CHOICES)
    time_create = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Categories, through='PostCategories')
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating_post = models.IntegerField(default=0)

    def preview(self):
        snippet = self.content[:124]
        if len(self.content) > 124:
            # обрезаем до последнего пробела
            snippet = snippet.rsplit(' ', 1)[0]
            return snippet + '...'
        return snippet
    

    def like(self):
        self.rating_post += 1
        self.save()
        self.author.update_rating()

    def dislike(self):
        self.rating_post -= 1
        self.save()
        self.author.update_rating()




class PostCategories(models.Model):
    categories = models.ForeignKey(Categories, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True)
    rating_comment = models.IntegerField(default=0)

    def like(self):
        self.rating_comment += 1
        self.save()
        self.post.author.update_rating()

    def dislike(self):
        self.rating_comment -= 1
        self.save()
        self.post.author.update_rating()








