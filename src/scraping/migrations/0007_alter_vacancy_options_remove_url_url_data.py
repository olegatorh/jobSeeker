# Generated by Django 4.2.4 on 2023-09-12 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0006_alter_errors_options_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vacancy',
            options={'ordering': ['-timestamp'], 'verbose_name': 'назва вакансії', 'verbose_name_plural': 'вакансії'},
        ),
        migrations.RemoveField(
            model_name='url',
            name='url_data',
        ),
    ]