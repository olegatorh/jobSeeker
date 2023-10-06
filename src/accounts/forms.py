from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

from scraping.models import Location, Search

User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Імейл')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='пароль')

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get('email').strip()
        password = self.cleaned_data.get('password').strip()

        if email and password:
            qs = User.objects.filter(email=email)
            if not qs.exists():
                raise forms.ValidationError('Такого користувача немає')
            if not check_password(password, qs[0].password):
                raise forms.ValidationError('Пароль не підходить')
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Користувач відключений')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='введіть пошту', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='введіть пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='повторіть пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')

    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError('паролі не співпадають!')
        return data['password2']


class UserUpdateForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), to_field_name='slug', required=False,
                                      widget=forms.Select(attrs={
                                          'class': 'form-control'
                                      }), label='Локація', empty_label="")
    search = forms.ModelChoiceField(queryset=Search.objects.all(), to_field_name='slug', required=True,
                                    widget=forms.Select(attrs={'class': 'form-control'
                                    }), label='Пошук', empty_label="")
    newsletter = forms.BooleanField(required=False, widget=forms.CheckboxInput, label='отримувати розсилку')

    class Meta:
        model = User
        fields = ('location', 'search', 'newsletter')

