from django.core.management.base import BaseCommand
from cam.models import UserProfile, Image, Comment, Like
from faker import Faker
import random
import os

class Command(BaseCommand):
    help = 'Populate database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        for i in range(10):
            user = UserProfile.objects.create(
                username=fake.user_name(),
                email=fake.email(),
                password=fake.password(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text()
            )
            for j in range(5):
                image = Image.objects.create(
                    user=user,
                    image="images/deneme/deneme_vuuxPFa.webp",
                    description="bu bir denemedir",
                    is_edited=True,
                )
                for k in range(3):
                    Comment.objects.create(
                        user=user,
                        image=image,
                        comment=fake.text()
                    )
                    Like.objects.create(
                        user=user,
                        image=image
                    )
        self.stdout.write(self.style.SUCCESS('Successfully populated database'))