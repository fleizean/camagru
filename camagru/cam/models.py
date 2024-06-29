from email.mime.image import MIMEImage
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.html import mark_safe
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from camagru.settings import EMAIL_HOST_USER, BASE_URL, STATICFILES_DIRS
from .utils import get_upload_to, get_upload_to_image
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
    is_verified = models.BooleanField(default=False)
    is_email_notification = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.username}"

    
    @property
    def thumbnail(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.avatar.url))

class Image(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_to_image)
    description = models.CharField(max_length=255, blank=True, null=True)
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

class VerifyToken(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def send_verification_email(self, request, user):
        token = VerifyToken.objects.get(user=user)
        mail_subject = 'Activate your account.'
        message = render_to_string('activate_account_email.html', {
            'user': user,
            'domain': request.META['HTTP_HOST'],
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

        # List of images
        images = ['github.png', '268a.png', 'back.png', 'head.png']

        for img_name in images:
            img_path = os.path.join(STATICFILES_DIRS[0], "assets", "email", img_name)

            # Open the image file in binary mode
            with open(img_path, 'rb') as f:
                image_data = f.read()

            # Create a MIMEImage
            img = MIMEImage(image_data)

            # Add a 'Content-ID' header. The angle brackets are important.
            img.add_header('Content-ID', f'<{img_name}>')

            # Attach the image to the email
            email.attach(img)

        # Send the email
        email.send(fail_silently=True)
        #send_mail(mail_subject, message, EMAIL_HOST_USER, [user.email], fail_silently=True, html_message=message)

