# Generated by Django 5.0 on 2024-11-17 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_faq'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='question',
            field=models.CharField(max_length=255),
        ),
    ]
