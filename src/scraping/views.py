from django.core.paginator import Paginator
from django.shortcuts import render

from .forms import FindForm
from .models import Vacancy


# Create your views here.
def home_view(request):
    form = FindForm()
    return render(request, 'scraping/home.html', {'form': form})


# Create your views here.
def list_view(request):
    location = request.GET.get('location')
    search = request.GET.get('search')
    # with_salary = request.POST.get('with_salary')
    context = {'search': search, 'location': location}


    if location or search:
        _filter = {}
        if location:
            _filter['location__slug'] = location
        if search:
            _filter['search__slug'] = search

        qs = Vacancy.objects.filter(**_filter)
        paginator = Paginator(qs, 12, )
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['object_list'] = page_obj
        context['first_page'] = page_obj.paginator.get_page(1).number

    return render(request, 'scraping/list.html', context)
