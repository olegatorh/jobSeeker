from django.db import models
from slugify import slugify


def default_urls():
    return {"work": "", "rabota": "", "dou": "", "djinni": ""}


class Location(models.Model):
    name = models.CharField(max_length=50, verbose_name='локація', unique=True)
    slug = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = 'локація'
        verbose_name_plural = 'локації'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)


class Search(models.Model):
    name = models.CharField(max_length=50, verbose_name='назва пошуку', unique=True)
    slug = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'пошук'
        verbose_name_plural = 'пошук'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Search, self).save(*args, **kwargs)


class Vacancy(models.Model):
    url = models.URLField(unique=True, verbose_name='посилання')
    title = models.CharField(max_length=100, verbose_name='назва вакансії')
    company = models.CharField(max_length=50, verbose_name='компанія')
    description = models.TextField(verbose_name='опис')
    salary = models.CharField(max_length=50, verbose_name='оплата', blank=True, null=True)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, null=True)
    search = models.ForeignKey('Search', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'назва вакансії'
        verbose_name_plural = 'вакансії'
        ordering = ['-timestamp']

    def __str__(self):
        return self.title


class Errors(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    class Meta:
        verbose_name = 'Помилка'
        verbose_name_plural = 'Помилки'

    def __str__(self):
        return str(self.timestamp)


class Url(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    search = models.ForeignKey('Search', on_delete=models.CASCADE)

    class Meta:
        unique_together = ("location", "search")
