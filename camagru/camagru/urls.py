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
from cam.views import login_view, signup, forgot_password, activate_account, about, privacy_policy_gpdr, home, logout_view, search_profiles

urlpatterns = [
    path('admin/', admin.site.urls),
    path('activate/<str:token>/', activate_account, name='activate'),
    path('', login_view, name='login'),
    path('login', login_view, name='login'),
    path('signup', signup, name='signup'),
    path('forgot-password', forgot_password, name='forgot-password'),
    path('about', about, name='about'),
    path('privacy-policy-gdpr', privacy_policy_gpdr, name='privacy-policy-gdpr'),
    path('home', home, name='home'),
    path('search_profiles/', search_profiles, name='search_profiles'),
    path('logout', logout_view, name='logout'),
]

handler404 = 'cam.views.handler404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)