# Generated by Django 4.2.4 on 2023-09-11 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0002_alter_vacancy_salary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='salary',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='оплата'),
        ),
    ]
