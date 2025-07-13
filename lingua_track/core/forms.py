from django import forms
from core.models import Card, TelegramLink
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['word', 'translation', 'example', 'notes', 'difficulty']
        widgets = {
            'word': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите слово'}),
            'translation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите перевод'}),
            'example': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите пример'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите заметки'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
        }


class TelegramLinkForm(forms.ModelForm):
    class Meta:
        model = TelegramLink
        fields = ['telegram_id']
        widgets = {
            'telegram_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваш Telegram ID'}),
        }


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Введите действительный email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите пароль'}),
        }