import asyncio, os, hashlib
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.core.files.base import ContentFile
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse


def delete_from_media(path):
    if os.path.isfile(path):
        os.remove(path)

def get_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s_%s.%s" % (instance.username, get_random_string(length=7), ext)
    return filename


def create_random_svg(username):
    hash = hashlib.md5(username.encode()).hexdigest()
    hue = int(hash, 16) % 360
    svg_parts = []
    for i in range(25 if username else 0):
        if int(hash, 16) & (1 << (i % 15)):
            x = 7 - i // 5 if i > 14 else i // 5
            svg_parts.append(f'<rect x="{x}" y="{i % 5}" width="1" height="1"/>')
    svg_content = f'''
    <svg viewBox="-1.5 -1.5 8 8" xmlns="http://www.w3.org/2000/svg" fill="hsl({hue}, 95%, 45%)">
    {''.join(svg_parts)}
    </svg>
    '''
    return ContentFile(svg_content.encode('utf-8'))

def get_upload_to_image(instance, filename):
    ext = filename.split('.')[-1]
    # Kullanıcı adını içeren bir klasör yolu ekleyerek güncelleme
    folder_name = "images/%s" % instance.user.username
    filename = "%s/%s_%s.%s" % (folder_name, instance.user.username, get_random_string(length=7), ext)
    return filename


def manual_model_to_dict(instance):
    return {field.name: getattr(instance, field.name) for field in instance._meta.fields}

def manual_get_object_or_404(klass, *args, **kwargs):
    try:
        return klass.objects.get(*args, **kwargs)
    except klass.DoesNotExist:
        raise Http404("No %s matches the given query." % klass._meta.object_name)

def manual_render(request, template_name, context=None, content_type=None, status=None, using=None):
    content = render_to_string(template_name, context, request=request, using=using)
    return HttpResponse(content, content_type=content_type, status=status)

def manual_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def manual_never_cache(view_func):
    def _wrapped_view(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Cache-Control'] = 'post-check=0, pre-check=0'
        response['Pragma'] = 'no-cache'
        return response
    return _wrapped_view

def manual_add_message(request, level, message):
    messages.add_message(request, level, message)

def manual_display_messages(request):
    for message in messages.get_messages(request):
        print(message)

def manual_create_content_file(content, name):
    return ContentFile(content, name=name)

def manual_urlsafe_base64_decode(s):
    return urlsafe_base64_decode(s)

def manual_generate_token(user):
    return default_token_generator.make_token(user)

def manual_update_session_auth_hash(request, user):
    update_session_auth_hash(request, user)

def manual_reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None):
    return reverse(viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
