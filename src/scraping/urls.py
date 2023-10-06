from django.urls import path

from .views import list_view, home_view

urlpatterns = [
    path('list/', list_view, name='list'),
    path('', home_view, name='home'),
    # path('with_sallary/', home_view, name='with_salary')
]
