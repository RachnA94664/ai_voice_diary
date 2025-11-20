from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    # Extend the Django user model for future custom fields
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    is_premium = models.BooleanField(default=False)  # Track premium status

    def __str__(self):
        return f'{self.user.username} Profile'
