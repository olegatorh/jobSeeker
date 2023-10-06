from django.contrib import admin
from .models import Location, Search, Vacancy, Errors, Url

# Register your models here.

admin.site.register(Search)
admin.site.register(Location)
admin.site.register(Vacancy)
admin.site.register(Errors)
admin.site.register(Url)
