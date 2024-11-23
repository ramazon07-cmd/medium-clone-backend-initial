# Generated by Django 4.2 on 2024-11-23 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0019_alter_article_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('publish', 'Publish'), ('draft', 'Draft')], max_length=50),
        ),
    ]
