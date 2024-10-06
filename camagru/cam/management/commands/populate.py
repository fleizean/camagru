from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
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
                password=make_password(fake.password()),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text()
            )
            for j in range(5):
                image = Image.objects.create(
                    user=user,
                    image="images/Kandirali/Kandirali_oTfEKVw.png",
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
        
        user = UserProfile.objects.create(
            username="fleizean",
            email="nsyagz@gmail.com",
            password=make_password("415263Enes."),
            first_name="Enes",
            last_name="Yagiz",
            bio="I'm a software developer.",
            is_verified=True
        )

        image = Image.objects.create(
            user=user,
            image="images/Kandirali/Kandirali_oTfEKVw.png",
            description="bu bir denemedir",
            is_edited=True,
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database'))