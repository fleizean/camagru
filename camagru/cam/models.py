import mimetypes
from email.mime.image import MIMEImage
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.html import mark_safe
from django.template.loader import render_to_string
from email.mime.text import MIMEText
from django.core.mail import EmailMultiAlternatives
from camagru.settings import EMAIL_HOST_USER, BASE_URL, STATICFILES_DIRS
from .utils import get_upload_to, get_upload_to_image, create_random_svg
from django.utils import timezone
import uuid
from datetime import timedelta
import os
import random

# Create your models here.

class UserProfile(AbstractUser):
    displayname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, max_length=254)
    avatar = models.ImageField(upload_to=get_upload_to, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    folowers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followers')
    following = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='followings')
    is_verified = models.BooleanField(default=False)
    is_email_notification = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.username}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            svg_content = create_random_svg(self.username)
            self.avatar.save(f"{self.username}.svg", svg_content, save=False)
        super().save(*args, **kwargs)

    @property
    def thumbnail(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.avatar.url))

class Image(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_to_image)
    description = models.CharField(max_length=255, blank=True, null=True)
    effect = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def humanized_time(self):
        delta = timezone.now() - self.created_at
        if delta < timedelta(minutes=1):
            return "now"
        elif delta < timedelta(hours=1):
            return f"{delta.seconds // 60} m"
        elif delta < timedelta(days=1):
            return f"{delta.seconds // 3600} h"
        elif delta < timedelta(days=30):
            return f"{delta.days} d"
        else:
            return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def humanized_time(self):
        delta = timezone.now() - self.created_at
        if delta < timedelta(minutes=1):
            return "now"
        elif delta < timedelta(hours=1):
            return f"{delta.seconds // 60} m"
        elif delta < timedelta(days=1):
            return f"{delta.seconds // 3600} h"
        elif delta < timedelta(days=30):
            return f"{delta.days} d"
        else:
            return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    def send_mail(self, request, user, image):
        if not user.is_email_notification:
            return
    
        mail_subject = f'{request.user.username} replied to your image.'
        
        image_path = image.image.path if image.image else None
        
        
        if image_path and not os.path.isfile(image_path):
            print(f"Image file does not exist: {image_path}")
            return
    
        message = render_to_string('email_verification.html', {
            'user': request.user,
            'comment': self.comment,
            'url': BASE_URL,
            'image_cid': 'image1',
            'comment_count': image.comment_set.count(),
            'like_count': image.like_set.count(),
        })
    
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=message,
            from_email=EMAIL_HOST_USER,
            to=[user.email]
        )
    
        email.attach_alternative(message, "text/html")
    
        if image_path:
            mime_type, _ = mimetypes.guess_type(image_path)
            with open(image_path, 'rb') as img:
                if mime_type == 'image/svg+xml':
                    mime_image = MIMEText(img.read().decode('utf-8'), _subtype='svg+xml')
                else:
                    mime_image = MIMEImage(img.read(), _subtype=mime_type.split('/')[1] if mime_type else 'octet-stream')
                mime_image.add_header('Content-ID', '<image1>')
                email.attach(mime_image)
    
    
        email.send(fail_silently=False)
    
class Like(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class VerifyToken(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def send_verification_email(self, request, user):
        token = VerifyToken.objects.get(user=user)
        mail_subject = 'Activate your account.'
        message = render_to_string('activate_account_email.html', {
            'user': user,
            'domain': BASE_URL,
            'token': token.token,
        })
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=message,  # this is the simple text version
            from_email=EMAIL_HOST_USER,
            to=[user.email]
        )

        # Add the HTML version. This could be the same as the body if your email is only HTML.
        email.attach_alternative(message, "text/html")
        
        # Send the email
        email.send(fail_silently=True)

