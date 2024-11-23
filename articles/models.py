from django.db import models
from users.models import CustomUser
from ckeditor.fields import RichTextField

class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'topic' # database ma'lumotlari
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
        db_table = "comment"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]

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
    topics = models.ManyToManyField(Topic, related_name='articles', blank=True, null=True)
    claps = models.ManyToManyField(
        CustomUser,
        # through='ArticleClap',
        related_name='clapped_articles'
    )

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
        db_table = "favorite" # database ma'lumotlari
        unique_together = ('user', 'article')
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.article.title}"

class Clap(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'article')

    def __str__(self):
        return f'{self.user.username} - {self.article.title} - {self.count}'

class Report(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    class Meta:
        db_table = 'report'
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.message}'

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta:
        db_table = 'faq'
        verbose_name = "FAQ"
        verbose_name_plural = "FAQS"

    def __str__(self):
        return f'{self.question}'
