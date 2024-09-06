from django.db import models
from users.models import CustomUser
from ckeditor.fields import RichTextField

class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'topic'
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        ordering = ['name']
    def __str__(self):
        return self.name
class Comment(models.Model):
    article = models.ForeignKey(
        'Article',
        on_delete=models.CASCADE,
        related_name='article_comments'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_comments'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"

    class Meta:
        ordering = ['created_at']

class Article(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = RichTextField()
    title = models.CharField(max_length=255)
    summary = models.TextField()
    status = models.CharField(max_length=50, choices=[('publish', 'Publish'), ('draft', 'Draft')])
    thumbnail = models.ImageField(upload_to='articles/thumbnails/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    reads_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.ManyToManyField(Comment, related_name='comments', blank=True)
    topics = models.ManyToManyField(Topic, related_name='articles', blank=True)
    claps = models.ManyToManyField(CustomUser, related_name='clapped_articles', blank=True)

    class Meta:
        db_table = 'article' # article table ning nomi
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class TopicFollow(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'topic')

class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorite"
        unique_together = ('user', 'article')
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.article.title}"