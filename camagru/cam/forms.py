from datetime import timedelta
from email.mime.image import MIMEImage
import os
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from camagru.settings import EMAIL_HOST_USER, STATICFILES_DIRS
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm 
from .models import Image, UserProfile, Comment, Like
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

class UserProfileForm(UserCreationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'input'}))
    displayname = forms.CharField(label='Displayname', widget=forms.TextInput(attrs={'class': 'input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'input'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'input'}))
    password2 = forms.CharField(label='RePassword', widget=forms.PasswordInput(attrs={'class': 'input'}))
    avatar = forms.ImageField(required=False ,label='Avatar', widget=forms.FileInput(attrs={'class': 'input'}))

    class Meta:
        model = UserProfile
        fields = ['username', 'displayname', 'email', 'password1', 'password2', 'avatar']

class DeleteAccountForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(DeleteAccountForm, self).__init__(*args, **kwargs)

class AuthenticationUserForm(AuthenticationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'input'}))
    class Meta:
        model = UserProfile
        fields = ['username', 'password']
        