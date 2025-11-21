from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()


# ===============================
#        DIARY ENTRY
# ===============================
class DiaryEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    ENTRY_TYPE_CHOICES = [
        ('voice', 'Voice'),
        ('text', 'Text'),
    ]
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES, default='text')

    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)

    PROCESSING_MODE_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
    ]
    processing_mode = models.CharField(max_length=10, choices=PROCESSING_MODE_CHOICES, default='free')

    ai_sentiment = models.CharField(max_length=20, null=True, blank=True)
    ai_insights = models.TextField(null=True, blank=True)

    total_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='processing')

    def __str__(self):
        return f"{self.user.username} Entry {self.created_at}"


# Auto-create UserProfile after user signup
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# ===============================
#       ADVANCED EXPENSE
# ===============================
class Expense(models.Model):

    EXPENSE_CATEGORIES = [
        ('food', 'Food & Beverages'),
        ('groceries', 'Groceries'),
        ('transport', 'Transport'),
        ('fuel', 'Fuel / Petrol / Diesel'),
        ('travel', 'Travel & Trips'),
        ('shopping', 'Shopping'),
        ('clothing', 'Clothing & Accessories'),
        ('electronics', 'Electronics'),
        ('subscriptions', 'Subscriptions'),
        ('entertainment', 'Entertainment'),
        ('health', 'Health & Medical'),
        ('fitness', 'Fitness / Gym'),
        ('education', 'Education / Courses'),
        ('books', 'Books & Stationery'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent / Accommodation'),
        ('maintenance', 'Home Maintenance'),
        ('personal', 'Personal Care'),
        ('beauty', 'Beauty & Salon'),
        ('gifts', 'Gifts & Donations'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes'),
        ('business', 'Business Expenses'),
        ('restaurant', 'Restaurant / Dining'),
        ('fast_food', 'Fast Food'),
        ('coffee', 'Coffee / Snacks'),
        ('pharmacy', 'Pharmacy'),
        ('mobile', 'Mobile Recharge / Bills'),
        ('internet', 'Internet / Broadband'),
        ('parking', 'Parking Charges'),
        ('car_service', 'Car / Bike Service'),
        ('ride_sharing', 'Uber / Ola / Taxi'),
        ('investment', 'Investments'),
        ('pet', 'Pet Care'),
        ('kids', 'Kids / Childcare'),
        ('misc', 'Miscellaneous'),
        ('other', 'Other'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI / Wallet'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    diary_entry = models.ForeignKey(
        DiaryEntry,
        on_delete=models.CASCADE,
        related_name='diary_expenses'   # Correct related_name
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='INR')

    category = models.CharField(max_length=32, choices=EXPENSE_CATEGORIES, default='other')
    payment_method = models.CharField(max_length=16, choices=PAYMENT_METHODS, default='upi')

    merchant = models.CharField(max_length=100, blank=True, null=True)
    detected_text = models.TextField(blank=True)
    confidence_score = models.FloatField(default=0.7)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} {self.currency} - {self.category}"
