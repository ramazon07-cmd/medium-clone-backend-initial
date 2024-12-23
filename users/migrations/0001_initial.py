# Generated by Django 5.0 on 2024-09-09 10:02

import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.indexes
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import django_resized.forms
import users.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('articles', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('first_name_en', models.CharField(blank=True, max_length=150, null=True, verbose_name='first name')),
                ('first_name_uz', models.CharField(blank=True, max_length=150, null=True, verbose_name='first name')),
                ('first_name_ru', models.CharField(blank=True, max_length=150, null=True, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('last_name_en', models.CharField(blank=True, max_length=150, null=True, verbose_name='last name')),
                ('last_name_uz', models.CharField(blank=True, max_length=150, null=True, verbose_name='last name')),
                ('last_name_ru', models.CharField(blank=True, max_length=150, null=True, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('middle_name', models.CharField(blank=True, max_length=30, null=True)),
                ('middle_name_en', models.CharField(blank=True, max_length=30, null=True)),
                ('middle_name_uz', models.CharField(blank=True, max_length=30, null=True)),
                ('middle_name_ru', models.CharField(blank=True, max_length=30, null=True)),
                ('avatar', django_resized.forms.ResizedImageField(blank=True, crop=['top', 'left'], force_format=None, keep_meta=True, quality=80, scale=1, size=[300, 300], upload_to=users.models.file_upload)),
                ('birth_year', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2024)])),
                ('following', models.ManyToManyField(related_name='followers_set', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'user',
                'ordering': ['-date_joined'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('followee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower_set', to=settings.AUTH_USER_MODEL)),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReadingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('less_recommend', models.ManyToManyField(related_name='less_recommend', to='articles.article')),
                ('more_recommend', models.ManyToManyField(related_name='more_recommend', to='articles.article')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Recommendation',
                'verbose_name_plural': 'Recommendations',
                'db_table': 'recommendation',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=django.contrib.postgres.indexes.HashIndex(fields=['first_name'], name='customuser_first_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=django.contrib.postgres.indexes.HashIndex(fields=['last_name'], name='customuser_last_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=django.contrib.postgres.indexes.HashIndex(fields=['middle_name'], name='customuser_middle_name_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['username'], name='customuser_username_idx'),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.CheckConstraint(check=models.Q(('birth_year__gt', 1900), ('birth_year__lt', 2024)), name='check_birth_year_range'),
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('follower', 'followee')},
        ),
        migrations.AlterUniqueTogether(
            name='readinghistory',
            unique_together={('user', 'article')},
        ),
    ]
