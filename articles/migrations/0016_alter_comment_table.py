# Generated by Django 4.2 on 2024-11-23 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0015_remove_article_user_alter_article_author'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='comment',
            table='comment',
        ),
    ]
