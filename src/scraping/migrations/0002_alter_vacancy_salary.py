# Generated by Django 4.2.4 on 2023-09-11 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='salary',
            field=models.CharField(blank=True, max_length=50, verbose_name='оплата'),
        ),
    ]