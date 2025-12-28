from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom d’utilisateur'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe'
        })
    )


class SignupForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom d’utilisateur'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmer le mot de passe'
        })
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')
