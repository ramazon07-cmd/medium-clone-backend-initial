# Generated by Django 4.2 on 2024-11-23 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_customuser_popularity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='popularity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
