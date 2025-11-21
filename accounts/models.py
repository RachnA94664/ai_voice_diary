from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# ===============================
#       CUSTOM USER MODEL
# ===============================
class User(AbstractUser):
    """Extend Django User if needed in future."""
    pass


# ===============================
#       USER PROFILE MODEL
# ===============================
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Optional user bio
    bio = models.TextField(blank=True)

    # Premium system fields
    is_premium = models.BooleanField(default=False)
    trial_start_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)

    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('trial', 'Trial'),
        ('premium', 'Premium'),
    ]
    subscription_type = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_CHOICES,
        default='free'
    )

    # Chat limits
    chat_questions_today = models.IntegerField(default=0)
    chat_questions_date = models.DateField(null=True, blank=True)

    # Diary entry count
    entry_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} Profile"
