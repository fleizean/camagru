import os
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.http import Http404
from django.db.models.aggregates import Count
from random import randint
from .models import (
    VerifyToken,
    UserProfile,
    Image,
    Comment,
    Like,
)

from .forms import (
    UserProfileForm,
    DeleteAccountForm,
    AuthenticationUserForm,
)

from os import environ
from datetime import datetime, timedelta
from django.utils.http import urlsafe_base64_decode
from django.utils import timezone
import urllib.parse
import urllib.request
from urllib.parse import urlencode
import json
from django.core.files import File
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from camagru.settings import EMAIL_HOST_USER, BASE_URL, STATICFILES_DIRS
import random

# Create your views here.

def handler404(request, exception):
    return render(request, "404.html", status=404)

@never_cache
def login_view(request):
    if request.user.is_authenticated:
       return redirect('home')
    error = None
    if request.method == "POST":
        form = AuthenticationUserForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            """  if not user.is_verified: #TODO confirm_login_allowed make this unnecessary?
                messages.error(request, "Account not verified")
                return redirect('login') """
            login(request, user)
            return HttpResponseRedirect("home")
        else:
            error = "Invalid username or password"
    else:
        form = AuthenticationUserForm()
    return render(request,"login.html", {"form": form, "error": error})

@never_cache
def signup(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            obj = VerifyToken.objects.create(
                user=user, token=default_token_generator.make_token(user)
            )
            obj.send_verification_email(request, user)
            return HttpResponseRedirect("login")
    else:
        form = UserProfileForm()
    return render(request, "signup.html", {"form": form})

@never_cache
def forgot_password(request):
    return render(request, "forgot-password.html")

@never_cache
def activate_account(request, token):
    try:
        token = VerifyToken.objects.get(token=token)
    except VerifyToken.DoesNotExist:
        return render(request, "activation_fail.html")
    token.user.is_verified = True
    token.user.save()
    token.delete()
    messages.success(request, "Your account has been verified.")
    login(request, token.user)
    return redirect("profile", request.user.username)

@never_cache
def about(request):
    return render(request, "about.html")

@never_cache
def privacy_policy_gpdr(request):
    return render(request, "privacy-policy-gdpr.html")

@never_cache
def logout_view(request):
    logout(request)
    return redirect("login")

def humanize_time_diff(target_time):
    now = timezone.now()
    diff = now - target_time
    
    days = diff.days
    seconds = diff.seconds
    minutes = seconds // 60
    hours = seconds // 3600
    if days > 7:
        return f"{days // 7} w"
    elif days > 0:
        return f"{days} d"
    elif hours > 0:
        return f"{hours} hrs"
    elif minutes > 0:
        return f"{minutes} min"
    else:
        return "now"

@never_cache
@login_required
def home(request):
    count = UserProfile.objects.aggregate(count=Count('id'))['count']
    
    if count > 4:
        user_profiles = UserProfile.objects.exclude(username=request.user.username).order_by('?')[:4]
    else:
        # Yeterli UserProfile yoksa, mevcut tümünü al
        user_profiles = UserProfile.objects.all()

    # Her UserProfile için en son paylaşılan fotoğrafı ve bu fotoğrafa ait like/comment bilgilerini al
    profile_data = []
    for profile in user_profiles:
        # En son paylaşılan fotoğrafı al
        image = Image.objects.filter(user=profile).order_by('-created_at').first()
        
        if image:  # Eğer fotoğraf varsa
            images_data = {
                'image': image.image.url,
                'description': image.description,
                'comments': image.comment_set.first(),
                'comments_count': image.comment_set.count(),
                'likes': image.like_set.count(),
                'is_liked': image.like_set.filter(user=request.user).exists(),
                'humanize_time_diff': humanize_time_diff(image.created_at),
            }
            
            profile_data.append({
                'profile': profile,
                'images_data': images_data
            })
    print(profile_data)
    return render(request, "home.html", {"user_profiles": user_profiles, "profile_data": profile_data})