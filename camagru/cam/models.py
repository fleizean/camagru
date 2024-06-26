from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.html import mark_safe
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from indianpong.settings import EMAIL_HOST_USER, BASE_URL
from .utils import get_upload_to
from django.utils import timezone
import uuid
from datetime import timedelta

# Create your models here.

class UserProfile(AbstractUser):
    displayname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, max_length=254)
    avatar = models.ImageField(upload_to=get_upload_to, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_42student = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.username}"
    
    @property
    def thumbnail(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.avatar.url))

class Image(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class UserPreference(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    email_notification = models.BooleanField(default=True)
    push_notification = models.BooleanField(default=True)