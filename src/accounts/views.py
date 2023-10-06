import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect

# Create your views here.
from .forms import UserLoginForm, UserRegistrationForm, UserUpdateForm
from scraping.run_scraping_once import start
User = get_user_model()


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        messages.success(request, 'користувач добавлений')
        return render(request, 'accounts/register_done.html', {'new_user': new_user})
    return render(request, 'accounts/register.html', {'form': form})


def update_view(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            form = UserUpdateForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user.search = data['search']
                user.location = data['location']
                user.newsletter = data['newsletter']
                user.save()
                messages.success(request, 'налаштування змінено')
                start(data['search'], data['location'])
                return redirect('accounts:update')
        else:
            form = UserUpdateForm(
                initial={'location': user.location, 'search': user.search, 'newsletter': user.newsletter})

            return render(request, 'accounts/update.html', {'form': form})
    else:
        return redirect('accounts:login')


def delete_view(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            qs = User.objects.get(pk=user.pk)
            qs.delete()
            messages.error(request, 'користувача видалено!')
    return redirect('accounts:login')