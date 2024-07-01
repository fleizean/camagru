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
from camagru.settings import EMAIL_HOST_USER, STATICFILES_DIRS, BASE_URL
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm 
from .models import Image, UserProfile, Comment, Like,VerifyToken
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
        
class PasswordResetUserForm(PasswordResetForm):
    def save(self, domain_override=None, token_generator=default_token_generator, request=None):
        email = self.cleaned_data["email"]
        # check if user exists with given email
        user = UserProfile.objects.filter(email=email).first()
        if user is None:
            self.add_error('email', 'User does not exist with this email.')
            return
        token = token_generator.make_token(user)
        VerifyToken.objects.create(user=user, token=token)
        mail_subject = 'Reset your password'
        message = render_to_string('password_reset_email.html', {
            'user': user,
            'domain': BASE_URL,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token,
        })

        
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=message,  # this is the simple text version
            from_email=EMAIL_HOST_USER,
            to=[user.email]
        )

        # Add the HTML version. This could be the same as the body if your email is only HTML.
        email.attach_alternative(message, "text/html")
        email.send(fail_silently=True)

class SetPasswordUserForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class': 'input'}))
    new_password2 = forms.CharField(label='Re New Password', widget=forms.PasswordInput(attrs={'class': 'input'}))

    class Meta:
        model = UserProfile
        fields = ['new_password1', 'new_password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            VerifyToken.objects.filter(user=user).delete()
        return user

class SetUserProfileForm(UserChangeForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'input'}))
    displayname = forms.CharField(label='Displayname', widget=forms.TextInput(attrs={'class': 'input'}))
    bio = forms.CharField(label='Bio', widget=forms.Textarea(attrs={'class': 'input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'input'}))
    avatar = forms.ImageField(required=False, label='Avatar', widget=forms.FileInput(attrs={'class': 'input'}))
    is_email_notification = forms.BooleanField(label='Email Notification', required=False, widget=forms.CheckboxInput(attrs={'class': 'input'}))
    password = forms.CharField(label='Password', required=False, widget=forms.PasswordInput(attrs={'class': 'input'}))

    class Meta:
        model = UserProfile
        fields = ['username', 'displayname', 'bio', 'email', 'avatar', 'is_email_notification', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            # Return None or an empty string if password is not provided
            return None
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Şifre alanı doluysa yeni şifreyi hashleyip set et
        else:
            # Şifre alanı boşsa, kullanıcı profilindeki mevcut şifreyi koru
            user.password = UserProfile.objects.get(pk=user.pk).password
        if commit:
            user.save()
        return user
