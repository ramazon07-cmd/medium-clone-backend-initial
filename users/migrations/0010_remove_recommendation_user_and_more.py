# Generated by Django 5.0 on 2024-09-03 04:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_recommendation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recommendation',
            name='user',
        ),
        migrations.AlterModelTable(
            name='recommendation',
            table='recommendation',
        ),
    ]
