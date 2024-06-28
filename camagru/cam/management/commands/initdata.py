from django.core.management.base import BaseCommand
from cam.models import UserProfile
from django.core.files import File
from os import environ
import json

class Command(BaseCommand):
	help = 'Description of what the command does'

	def handle(self, *args, **options):
		superuser = environ.get("SUPER_USER", default="Kandirali")
		supermail = environ.get("SUPER_MAIL", default="kan@g.com")
		superpass = environ.get("SUPER_PASS", default="9247")
		if not UserProfile.objects.filter(username=superuser).exists():
			super_user = UserProfile.objects.create_superuser(superuser, supermail, superpass)
			file = File(open('static/assets/profile-photos/default-photo.png', "rb"))
			super_user.avatar.save(f"{file.name}.png", file, save=False)
			file.close()
			super_user.indian_wallet = 1000
			super_user.save()
			self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))