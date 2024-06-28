from django import forms
from django.contrib import admin
from .models import UserProfile, Image, Comment, Like
from django.utils.html import format_html
from django.forms import ModelChoiceField

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'displayname', 'email', 'is_verified', 'is_email_notification', 'thumbnail')
    list_display_links = ('username', 'displayname')
    search_fields = ('username', 'displayname', 'email')
    list_filter = ('is_verified', 'is_email_notification')
    readonly_fields = ('thumbnail',)
    fieldsets = (
        (None, {
            'fields': ('username', 'displayname', 'email', 'password', 'is_verified', 'is_email_notification', 'avatar')
        }),
    )

    def thumbnail(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />'.format(obj.avatar.url))
        else:
            return "No Avatar"

    
        