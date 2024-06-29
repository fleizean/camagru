import asyncio, os, hashlib
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.cache import cache

def delete_from_media(path):
    if os.path.isfile(path):
        os.remove(path)

def get_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s_%s.%s" % (instance.username, get_random_string(length=7), ext)
    return filename

def get_upload_to_image(instance, filename):
    ext = filename.split('.')[-1]
    # Kullanıcı adını içeren bir klasör yolu ekleyerek güncelleme
    folder_name = "images/%s" % instance.user.username
    filename = "%s/%s_%s.%s" % (folder_name, instance.user.username, get_random_string(length=7), ext)
    return filename