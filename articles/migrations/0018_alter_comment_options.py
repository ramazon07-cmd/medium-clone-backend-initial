# Generated by Django 4.2 on 2024-11-23 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0017_alter_comment_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created_at'], 'verbose_name': 'Comment', 'verbose_name_plural': 'Comments'},
        ),
    ]
