# Generated by Django 5.0 on 2024-11-17 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_report_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQS',
                'db_table': 'faq',
            },
        ),
    ]
