from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Extend default user if needed
    pass

class UserProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
