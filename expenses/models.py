from django.db import models
from diary.models import DiaryEntry

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
        related_name='expenses',
        null=True,
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    category = models.CharField(
        max_length=50,
        choices=EXPENSE_CATEGORIES,
        default='other'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='upi'
    )
    merchant = models.CharField(max_length=100, null=True, blank=True)
    detected_text = models.TextField(default='', blank=True)
    confidence_score = models.FloatField(default=1.0)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} {self.currency} - {self.category}"
