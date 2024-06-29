from django import forms
from django.contrib import admin
from .models import UserProfile, Image, Comment, Like
from django.utils.html import format_html
from django.forms import ModelChoiceField

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'displayname', 'email', 'is_verified', 'is_email_notification', 'thumbnail', 'bio')
    list_display_links = ('username', 'displayname')
    search_fields = ('username', 'displayname', 'email')
    list_filter = ('is_verified', 'is_email_notification')
    readonly_fields = ('thumbnail',)
    fieldsets = (
        (None, {
            'fields': ('username', 'displayname', 'email', 'password', 'is_verified', 'is_email_notification', 'avatar', 'bio')
        }),
    )

    def thumbnail(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />'.format(obj.avatar.url))
        else:
            return "No Avatar"

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image', 'description', 'created_at', 'is_deleted', 'is_edited')
    list_display_links = ('user', 'image')
    search_fields = ('user__username', 'description')
    list_filter = ('is_deleted', 'is_edited')
    readonly_fields = ('created_at',)  # 'image' alanını buradan çıkardık
    fieldsets = (
        (None, {
            'fields': ('user', 'image', 'description', 'created_at', 'is_deleted', 'is_edited')
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image', 'comment', 'created_at')
    list_display_links = ('user', 'image')
    search_fields = ('user__username', 'image__description', 'comment')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'image', 'comment', 'created_at')
        }),
    )

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'image', 'created_at')
    list_display_links = ('user', 'image')
    search_fields = ('user__username', 'image__description')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'image', 'created_at')
        }),
    )
        