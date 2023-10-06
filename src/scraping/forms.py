from django import forms

from .models import Location, Search


class FindForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), to_field_name='slug', required=False,
                                  widget=forms.Select(attrs={
                                      'class': 'form-control'
                                  }),  label='Локація', empty_label="")
    search = forms.ModelChoiceField(queryset=Search.objects.all(), to_field_name='slug', required=False,
                                      widget=forms.Select(attrs={
                                          'class': 'form-control'
                                      }), label='Пошук', empty_label="")
