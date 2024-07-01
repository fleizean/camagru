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
from django.core.serializers import serialize
from .models import (
    VerifyToken,
    UserProfile,
    Image,
    Comment,
    Like,
)

from .forms import (
    UserProfileForm,
    PasswordResetUserForm,
    DeleteAccountForm,
    AuthenticationUserForm,
    SetPasswordUserForm,
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
    if request.user.is_authenticated:
        return redirect("home")
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
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = PasswordResetUserForm(request.POST or None)
        if form.is_valid():
            form.save(request=request)
            return redirect("password_reset_done")
    else:
        form = PasswordResetUserForm()
    return render(request, "forgot-password.html")

@never_cache
def password_reset_done(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "password_reset_done.html")

@never_cache
def set_password(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect("home")
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        # token is valid, you can show the user a form to enter a new password
        if request.method == "POST":
            form = SetPasswordUserForm(user, request.POST)
            if form.is_valid():
                form.save()
                #messages.success(request, "Your password has been reset.")
                return redirect("login")
        else:
            form = SetPasswordUserForm(user)
        return render(request, "set_password.html", {"form": form})
    else:
        # invalid token
        #messages.error(request, "The reset password link is invalid.")
        return redirect("forgot_password")

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
    count = UserProfile.objects.aggregate(count=Count('id'))['count']
    
    if count > 5:
        user_profiles = UserProfile.objects.exclude(username=request.user.username).order_by('?')[:5]
    else:
        # Yeterli UserProfile yoksa, mevcut tümünü al
        user_profiles = UserProfile.objects.all().exclude(username=request.user.username)

    # Her UserProfile için en son paylaşılan fotoğrafı ve bu fotoğrafa ait like/comment bilgilerini al
    profile_data = []
    for profile in user_profiles:
        # En son paylaşılan fotoğrafı al
        image = Image.objects.filter(user=profile).order_by('-created_at').first()
        if image:  # Eğer fotoğraf varsa
            images_data = {
                'id': image.id,
                'image': image.image.url,
                'description': image.description,
                'first_comment': image.comment_set.first(),
                'comments': image.comment_set.all(),
                'comments_count': image.comment_set.count(),
                'humanized_time': image.humanized_time,
                'likes': image.like_set.count(),
                'is_liked': image.like_set.filter(user=request.user).exists(),
                'created_at': image.created_at
            }
            profile_data.append({
                'profile': profile,
                'images_data': images_data
            })
        is_followed = request.user.following.filter(id=profile.id).exists()
        profile.is_followed = is_followed

    return render(request, "home.html", {"user_profiles": user_profiles, "profile_data": profile_data})

def search_profiles(request):
    data = json.loads(request.body)
    query = data.get('query', '')

    # Filter user profiles based on the query
    profiles = UserProfile.objects.filter(username__icontains=query)

    # Serialize the profiles or manually build the JSON response
    profiles_json = serialize('json', profiles)
    return JsonResponse({'profiles': profiles_json}, safe=False)


def search(request):
    count = UserProfile.objects.aggregate(count=Count('id'))['count']
    
    if count > 4:
        user_profiles = UserProfile.objects.exclude(username=request.user.username).order_by('?')[:4]
    else:
        # Yeterli UserProfile yoksa, mevcut tümünü al
        user_profiles = UserProfile.objects.all()
    return render(request, "search.html", {"user_profiles": user_profiles})

@never_cache
def profile_view(request, username):
    user = get_object_or_404(UserProfile, username=username)
    images_list = Image.objects.filter(user=user).order_by('-created_at')
    user.is_followed = request.user.following.filter(id=user.id).exists()
    for image in images_list:
        image.is_liked_by_user = Like.objects.filter(user=request.user, image=image).exists()
    # Manuel Pagination
    page = request.GET.get('page', 1)  # Eğer 'page' parametresi yoksa varsayılan olarak 1 değerini kullan
    page = int(page) if str(page).isdigit() else 1  # Sayfa numarasını güvenli bir şekilde int'e çevir
    per_page = 3  # Her sayfada gösterilecek resim sayısı
    total_images = images_list.count()
    total_pages = (total_images + per_page - 1) // per_page  # Toplam sayfa sayısı
    page_numbers = list(range(1, total_pages + 1))

    # Sayfalama sınırlarını ayarla
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    images = images_list[start_index:end_index]

    return render(request, "profile.html", {
        "user": user,
        "images": images,
        "is_followed": user.is_followed,
        "image_count": total_images,
        "page_numbers": page_numbers,
        "page": page,
        "total_pages": total_pages,
    })

@never_cache
def profile_settings(request, username):
    if request.user.username != username:
        raise Http404
    user = get_object_or_404(UserProfile, username=username)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
    else:
        form = UserProfileForm(instance=user)
    return render(request, "profile-settings.html", {"form": form, "user": user})

@login_required
def follow_user(request):
    data = json.loads(request.body)
    username = data.get('username')
    action = data.get('action')
    if username and action:
        try:
            target_user = UserProfile.objects.get(username=username)
            if action == 'follow':
                request.user.following.add(target_user)
                target_user.followers.add(request.user)
            elif action == 'unfollow':
                request.user.following.remove(target_user)
                target_user.followers.remove(request.user)
            return JsonResponse({'status':'ok'})
        except UserProfile.DoesNotExist:
            return JsonResponse({'status':'error', 'message': 'User not found.'})
    return JsonResponse({'status':'error', 'message': 'Invalid request'})

def send_message_post(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated.'})

    data = json.loads(request.body)
    message = data.get('message')
    image_id = data.get('id')  # Mesajın gönderileceği resmin ID'si

    if message and image_id:
        try:
            # Resmi ve alıcı kullanıcıyı bul
            image = Image.objects.get(id=image_id)
            receiver_user = image.user

            # Mesajı Comment modeli olarak kaydet
            Comment.objects.create(user=user, image=image, comment=message)
            return JsonResponse({
                'status': 'ok',
                'comment': {
                    'username': user.username,
                    'avatar_url': user.avatar.url if user.avatar else None,
                    'comment': message
                }
            })
        except Image.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def like_post(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated.'})

    data = json.loads(request.body)
    image_id = data.get('id')
    action = data.get('action')

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                Like.objects.create(user=user, image=image)
            elif action == 'unlike':
                Like.objects.filter(user=user, image=image).delete()
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})