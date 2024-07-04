"""
URL configuration for camagru project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from cam.views import login_view, signup, forgot_password, activate_account, about, privacy_policy_gpdr, home, logout_view, search_profiles, search, profile_view, follow_user, send_message_post, like_post, password_reset_done, set_password, profile_settings, handler404, upload_image, save_photo

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('activate/<str:token>/', activate_account, name='activate'),
    path('login', login_view, name='login'),
    path('signup', signup, name='signup'),
    path('forgot-password', forgot_password, name='forgot-password'),
    path('about', about, name='about'),
    path('privacy-policy-gdpr', privacy_policy_gpdr, name='privacy-policy-gdpr'),
    path('home', home, name='home'),
    path('search_profiles/', search_profiles, name='search_profiles'),
    path('search', search, name='search'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('profile-settings/<str:username>/', profile_settings, name='profile_settings'),
    path('follow/', follow_user, name='follow'),
    path('send_message_post/', send_message_post, name='send_message_post'),
    path('like_post/', like_post, name='like_post'),
    path('password_reset_done/', password_reset_done, name='password_reset_done'),
    path('set_password/<str:uidb64>/<str:token>/', set_password, name='set_password'),
    path('upload-image', upload_image, name='upload_image'),
    path('save-photo', save_photo, name='save_photo'),
    path('logout', logout_view, name='logout'),
]

handler404 = 'cam.views.handler404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)