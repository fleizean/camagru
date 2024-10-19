import random
import json
import base64
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models.aggregates import Count
from random import randint
from django.core.serializers import serialize
from PIL import ImageSequence, Image as PilImage, ImageOps
from django.core.files.base import ContentFile
from io import BytesIO
from .models import VerifyToken, UserProfile, Image, Comment, Like
from .forms import UserProfileForm, PasswordResetUserForm, DeleteAccountForm, AuthenticationUserForm, SetPasswordUserForm, SetUserProfileForm
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from camagru.settings import EMAIL_HOST_USER, BASE_URL
from django.db.models import Q
from django.utils.http import urlencode

from .utils import (
    manual_model_to_dict,
    manual_get_object_or_404,
    manual_render,
    manual_login_required,
    manual_never_cache,
    manual_add_message,
    manual_create_content_file,
    manual_urlsafe_base64_decode,
    manual_generate_token,
    manual_update_session_auth_hash,
    manual_reverse
)

# Create your views here.

def handler404(request, exception):
    return manual_render(request, "404.html", status=404)

@manual_never_cache
def login_view(request):
    error = None
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = AuthenticationUserForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return HttpResponseRedirect("home")
        else:
            # Hata mesajlarını kontrol et
            if form.non_field_errors():
                error = form.non_field_errors()[0]
            else:
                error = "Invalid username or password"
    else:
        form = AuthenticationUserForm()
    return manual_render(request, "login.html", {"form": form, "error": error})

@manual_never_cache
def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            obj = VerifyToken.objects.create(
                user=user, token=manual_generate_token(user)
            )
            obj.send_verification_email(request, user)
            return HttpResponseRedirect("login")
    else:
        form = UserProfileForm()
    return manual_render(request, "signup.html", {"form": form})

@manual_never_cache
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
    return manual_render(request, "forgot-password.html")

@manual_never_cache
def password_reset_done(request):
    if request.user.is_authenticated:
        return redirect("home")
    return manual_render(request, "password_reset_done.html")

@manual_never_cache
def set_password(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect("home")
    try:
        uid = manual_urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordUserForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("login")
        else:
            form = SetPasswordUserForm(user)
        return manual_render(request, "set_password.html", {"form": form})
    else:
        return redirect("forgot_password")

@manual_never_cache
def activate_account(request, token):
    try:
        token = VerifyToken.objects.get(token=token)
    except VerifyToken.DoesNotExist:
        return manual_render(request, "activation_fail.html")
    token.user.is_verified = True
    token.user.save()
    token.delete()
    login(request, token.user)
    return redirect("profile", request.user.username)

@manual_never_cache
def about(request):
    return manual_render(request, "about.html")

@manual_never_cache
def privacy_policy_gpdr(request):
    return manual_render(request, "privacy-policy-gdpr.html")

@manual_never_cache
@manual_login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@manual_never_cache
@manual_login_required
def home(request):
    count = UserProfile.objects.aggregate(count=Count('id'))['count']
    following_users = request.user.following.all()
    following_users_ids = request.user.following.values_list('id', flat=True)

    # Önerilen kullanıcıları al (mevcut kullanıcı hariç, rastgele 5 kullanıcı)
    suggested_users = UserProfile.objects.exclude(username=request.user.username).filter(is_private=False).order_by('?')[:5]

    # Önerilen kullanıcılar için takip edilip edilmediğini kontrol et
    for user in suggested_users:
        user.is_followed = user.id in following_users_ids
    if following_users.exists():
        # Takip edilen kullanıcıların UserProfile'larını al
        user_profiles = UserProfile.objects.filter(id__in=following_users.values_list('id', flat=True))
    else:
        # Takip edilen kimse yoksa, mevcut sistem devam eder
        count = UserProfile.objects.aggregate(count=Count('id'))['count']
        if count > 5:
            user_profiles = UserProfile.objects.exclude(username=request.user.username).order_by('?')[:5]
        else:
            user_profiles = UserProfile.objects.all().exclude(username=request.user.username).filter(is_private=False)

    # Her UserProfile için en son paylaşılan fotoğrafı ve bu fotoğrafa ait like/comment bilgilerini al
    profile_data = []
    for profile in user_profiles:
        # En son paylaşılan fotoğrafı al
        image = Image.objects.filter(user=profile, is_edited=True).order_by('-created_at').first()
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
                'effect': image.effect,
                'is_liked': image.like_set.filter(user=request.user).exists(),
                'created_at': image.created_at
            }
            profile_data.append({
                'profile': profile,
                'images_data': images_data
            })

    return manual_render(request, "home.html", {"user_profiles": user_profiles, "profile_data": profile_data, "suggested_users": suggested_users})

@manual_login_required
def search_profiles(request):
    try:
        data = json.loads(request.body)
        query = data.get('query', '')

        # Kullanıcı profillerini sorgula
        profiles = UserProfile.objects.filter(Q(username__icontains=query) & ~Q(username__icontains="Kandirali"))

        # Profilleri serileştir
        profiles_json = serialize('json', profiles)
        profiles_data = json.loads(profiles_json)  # JSON formatını doğrulamak için serileştirilen veriyi deserialize et

        return JsonResponse({'profiles': profiles_data}, safe=False)
    except Exception as e:
        # Hata mesajını günlüğe kaydet
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
@manual_login_required
def search(request):
    count = UserProfile.objects.aggregate(count=Count('id'))['count']
    
    if count > 4:
        user_profiles = UserProfile.objects.exclude(username=request.user.username).order_by('?')[:4]
    else:
        # Yeterli UserProfile yoksa, mevcut tümünü al
        user_profiles = UserProfile.objects.all()
    return manual_render(request, "search.html", {"user_profiles": user_profiles})

@manual_never_cache
def gallery_images(request, username):
    user = manual_get_object_or_404(UserProfile, username=username)
    page = request.GET.get('page', 1)
    per_page = 5
    images_list = Image.objects.filter(user=user, is_edited=True).order_by('-created_at')
    paginator = Paginator(images_list, per_page)
    images = paginator.get_page(page)

    images_data = []
    for image in images:
        images_data.append({
            'id': image.id,
            'image_url': image.image.url,
            'description': image.description,
            'like_count': image.like_set.count(),
            'comment_count': image.comment_set.count(),
            'is_liked_by_user': image.is_liked_by_user,
            'effect': image.effect,
            'user': {
                'username': image.user.username,
                'avatar_url': image.user.avatar.url if image.user.avatar else None,
                'is_verified': image.user.is_verified,
            }
        })

    return JsonResponse({
        'images': images_data,
        'has_next': images.has_next()
    })

@manual_never_cache
def profile_view(request, username):
    user = manual_get_object_or_404(UserProfile, username=username)
    images_list = Image.objects.filter(user=user, is_edited=True).order_by('-created_at')
    
    # Kullanıcı giriş yapmışsa takip edilip edilmediğini kontrol et
    if request.user.is_authenticated:
        user.is_followed = request.user.following.filter(id=user.id).exists()
        for image in images_list:
            image.is_liked_by_user = Like.objects.filter(user=request.user, image=image).exists()
    else:
        user.is_followed = False
        for image in images_list:
            image.is_liked_by_user = False

    # Manuel Pagination
    page = request.GET.get('page', 1)  # Eğer 'page' parametresi yoksa varsayılan olarak 1 değerini kullan
    page = int(page) if str(page).isdigit() else 1  # Sayfa numarasını güvenli bir şekilde int'e çevir
    per_page = 5  # Her sayfada gösterilecek resim sayısı
    total_images = images_list.count()
    total_pages = (total_images + per_page - 1) // per_page  # Toplam sayfa sayısı
    page_numbers = list(range(1, total_pages + 1))

    # Sayfalama sınırlarını ayarla
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    images = images_list[start_index:end_index]

    return manual_render(request, "profile.html", {
        "user": user,
        "images": images,
        "is_followed": user.is_followed,
        "image_count": total_images,
        "page_numbers": page_numbers,
        "page": page,
        "total_pages": total_pages,
    })

@manual_never_cache
@manual_login_required
def profile_settings(request, username):
    if request.user.username != username:
        raise Http404
    user = manual_get_object_or_404(UserProfile, username=username)
    if request.method == "POST":
        form = SetUserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_user = form.save()
            if 'password' in form.changed_data:
                manual_update_session_auth_hash(request, updated_user)
            messages.success(request, "Profile updated successfully.")
            response = redirect(manual_reverse('profile_settings', kwargs={'username': updated_user.username}))
            response.set_cookie('status', 'success', max_age=10)
            return response
        else:
            response = redirect(manual_reverse('profile_settings', kwargs={'username': user.username}))
            response.set_cookie('status', 'error', max_age=10)
            return response
    else:
        form = SetUserProfileForm(instance=user)
    return manual_render(request, "profile-settings.html", {"form": form, "user": user})

@manual_login_required
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

@manual_login_required
def send_message_post(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated.'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'})
    message = data.get('message')
    image_id = data.get('id')  # Mesajın gönderileceği resmin ID'si

    if message and image_id:
        try:
            # Resmi ve alıcı kullanıcıyı bul
            image = Image.objects.get(id=image_id)
            receiver_user = image.user

            # Mesajı Comment modeli olarak kaydet
            comment_user = Comment.objects.create(user=user, image=image, comment=message)
            comment_user.send_mail(request, receiver_user, image)
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
        except Exception as e:
            # Genel hata yakalama ve günlüğe kaydetme
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@manual_login_required
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

@manual_login_required
def upload_image(request):
    images = Image.objects.filter(user=request.user, is_edited=True).order_by('-created_at')
    return manual_render(request, "upload_image.html", {"images": images})


@manual_login_required
def save_photo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = UserProfile.objects.get(username=request.user.username)
            
            base64_image = data.get('image')
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]
            else:
                return JsonResponse({'success': False, 'message': 'Invalid image data'}, status=400)
                        
            filter_name = data.get('filter')
            effect = data.get('effect')
            description = data.get('description')
            image_data = base64.b64decode(base64_image) # Base64 veriyi çöz
            image = PilImage.open(BytesIO(image_data)) # Resmi aç
            
            filter_path = 'static/assets/filters/' + filter_name
            filter_image = PilImage.open(filter_path)
            
            # Filtrenin GIF olup olmadığını kontrol et
            if filter_image.format == 'GIF':
                frames = [frame.copy() for frame in ImageSequence.Iterator(filter_image)] # GIF karesini ayır
                processed_frames = []
                
                for frame in frames: # Her bir kare için
                    # Filtre karesini ana resmin boyutuna sığdır
                    resized_frame = ImageOps.fit(frame, image.size, method=0, bleed=0.0, centering=(0.5, 0.5))
                    # Filtreyi her bir kareye uygula
                    combined_frame = PilImage.alpha_composite(image.convert("RGBA"), resized_frame.convert("RGBA"))
                    processed_frames.append(combined_frame)
                
                # İşlenmiş kareleri GIF olarak kaydet
                result_image_io = BytesIO()
                processed_frames[0].save(result_image_io, format='GIF', save_all=True, append_images=processed_frames[1:], loop=0, duration=filter_image.info['duration'], dispose=filter_image.info.get('dispose', 2))
            else:
                # Filtre GIF değilse, tek kareli resim için filtreyi uygula
                resized_filter = ImageOps.fit(filter_image, image.size, method=0, bleed=0.0, centering=(0.5, 0.5)) # Filtreyi ana resmin boyutuna sığdır
                combined_image = PilImage.alpha_composite(image.convert("RGBA"), resized_filter.convert("RGBA")) # Filtreyi ana resme uygula
                result_image_io = BytesIO() # Sonucu bir dosya nesnesine kaydet
                combined_image.save(result_image_io, format='PNG') # Sonucu PNG olarak kaydet
            
            result_image_content_file = manual_create_content_file(result_image_io.getvalue(), name='filtered_image.' + ('gif' if filter_image.format == 'GIF' else 'png'))
            
            if result_image_content_file.size > 3*1024*1024: # 3MB'dan büyükse
                return JsonResponse({'success': False, 'message': 'Image file size must be less than 3MB'}, status=400) # Hata döndür
            new_image = Image(user=user, image=result_image_content_file, description=description, is_edited=True, effect=effect) # Yeni bir Image nesnesi oluştur
            new_image.save()
            
            return JsonResponse({'success': False, 'message': 'Image saved successfully.'})
        except UnidentifiedImageError:
            return JsonResponse({'success': False, 'message': 'Cannot identify image file'}, status=400)
        except SuspiciousOperation as e:
            return JsonResponse({'success': False, 'message': 'Invalid file operation'}, status=400)
        except MemoryError as e:
            return JsonResponse({'success': False, 'message': 'File too large'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@manual_login_required
def deletePost(request):
    data = json.loads(request.body)
    image_id = data.get('id')
    if image_id:
        try:
            image = Image.objects.get(id=image_id)
            image.delete()
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})