from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Settings
from django import forms


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['private']


class CountryForm(forms.Form):
    OPTIONS = (
        ("bff", "Best friend"),
        ("f", "Friend")
    )
    friendShipStatus = forms.ChoiceField(
        label='Friendship status',
        widget=forms.Select(),
        choices=OPTIONS)
