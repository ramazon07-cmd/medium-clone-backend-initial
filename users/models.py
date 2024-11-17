from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField
import os
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core import validators
from users.errors import BIRTH_YEAR_ERROR_MSG
from django.contrib.postgres.indexes import HashIndex

def file_upload(instance, filename):
    """ bu funksiya orqali userga avatar qo'shiladi """
    ext = filename.split('.')[-1]
    filename = f'{instance.username}.{ext}'
    return os.path.join('users/avatars/', filename)

class CustomUser(AbstractUser):
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = ResizedImageField(size=[300, 300], crop=['top', 'left'], upload_to=file_upload, blank=True)
    birth_year = models.IntegerField(
        validators=[
            validators.MinValueValidator(settings.BIRTH_YEAR_MIN),
            validators.MaxValueValidator(settings.BIRTH_YEAR_MAX)
        ],
        null=True,
        blank=True
    )
    following = models.ManyToManyField(
        'self', related_name='followers_set', symmetrical=False, blank=True
    )

    def is_following(self, user):
        return self.following.filter(id=user.id).exists()

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
            self.save()
        else:
            raise ValidationError("You are already following this user.")

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
            self.save()
        else:
            raise ValidationError("You are not following this user.")

    def clean(self):
        super().clean()
        if self.birth_year is not None and not (settings.BIRTH_YEAR_MIN < self.birth_year < settings.BIRTH_YEAR_MAX):
            raise ValidationError(BIRTH_YEAR_ERROR_MSG)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]
        indexes = [
            HashIndex(fields=['first_name'], name='%(class)s_first_name_hash_idx'),
            HashIndex(fields=['last_name'], name='%(class)s_last_name_hash_idx'),
            HashIndex(fields=['middle_name'], name='%(class)s_middle_name_hash_idx'),
            models.Index(fields=['username'], name='%(class)s_username_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(birth_year__gt=settings.BIRTH_YEAR_MIN) & models.Q(
                    birth_year__lt=settings.BIRTH_YEAR_MAX),
                name='check_birth_year_range'
            )
        ]

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """Returns the full name of the user"""
        names = [self.first_name, self.middle_name, self.last_name]
        return " ".join([name for name in names if name])  # Filter out empty or None values


class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    more_recommend = models.ManyToManyField('articles.Article', related_name='more_recommend')
    less_recommend = models.ManyToManyField('articles.Article', related_name='less_recommend')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recommendation'
        verbose_name = "Recommendation"
        verbose_name_plural = "Recommendations"
        ordering = ['-created_at']

class ReadingHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey('articles.Article', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='follows', on_delete=models.CASCADE)
    followee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followed_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followee')

    def __str__(self):
        return f"{self.follower} follows {self.followee}"

class PinArticle(models.Model):
    pin = models.ForeignKey('Pin', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey('articles.Article', on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('pin', 'article')
        db_table = 'pin_article'

    def __str__(self):
        return f'{self.pin.user.username} - {self.article.title}'


class Pin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    articles = models.ManyToManyField('articles.Article', through='PinArticle', related_name='pin_articles')
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pin'
        verbose_name = "Pin"
        verbose_name_plural = "Pins"
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.count}'

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notification'
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.message}'
