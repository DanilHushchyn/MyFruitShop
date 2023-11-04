from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class MyAuthenticationForm(forms.Form):
    username = forms.CharField(label="", max_length=100, required=False,
                               widget=forms.TextInput(
                                   attrs={'placeholder': 'username', 'class': 'form-control'}))
    password = forms.CharField(label="", max_length=100, required=False,
                               widget=forms.PasswordInput(
                                   attrs={'placeholder': 'password', 'class': 'form-control'}))
