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

@never_cache
@login_required
def home(request):
    return render(request, "home.html")