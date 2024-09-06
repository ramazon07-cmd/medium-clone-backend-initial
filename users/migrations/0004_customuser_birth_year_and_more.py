# Generated by Django 5.0 on 2024-08-23 12:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0003_alter_customuser_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='birth_year',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2024)]),
        ),
        migrations.AddConstraint(
            model_name='customuser',
            constraint=models.CheckConstraint(check=models.Q(('birth_year__gt', 1900), ('birth_year__lt', 2024)), name='check_birth_year_range'),
        ),
    ]
