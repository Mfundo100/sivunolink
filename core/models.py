from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import random

# ==========================================
# 1. USER & PROFILE MANAGEMENT
# ==========================================
class User(AbstractUser):
    ROLE_CHOICES = (
        ('FARMER', 'Farmer'),
        ('BUYER', 'Urban Buyer'),
        ('DRIVER', 'Transport Driver'),
        ('ADMIN', 'Platform Admin'),
    )
    LANGUAGE_CHOICES = (('en', 'English'), ('sz', 'siSwati'))
    REGION_CHOICES = (
        ('HHOHHO', 'Hhohho'),
        ('MANZINI', 'Manzini'),
        ('SHISELWENI', 'Shiselweni'),
        ('LUBOMBO', 'Lubombo'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='BUYER')
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    
    # Driver Availability Toggle
    is_available = models.BooleanField(default=True, help_text="Toggle driver pickup availability")
    
    groups = models.ManyToManyField('auth.Group', related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name="custom_user_set", blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class FarmProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'FARMER'})
    farm_name = models.CharField(max_length=100, help_text="e.g., Potatoes")
    region = models.CharField(max_length=20, choices=User.REGION_CHOICES, default='MANZINI')
    town = models.CharField(max_length=100, help_text="e.g., Nhlangano")
    
    def __str__(self):
        return self.farm_name

class DriverProfile(models.Model):
    VEHICLE_TYPES = (
        ('KOMBI', 'Kombi'),
        ('TRUCK', 'Truck'),
        ('BAKKIE', 'Bakkie'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DRIVER'})
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='BAKKIE')
    capacity_kg = models.DecimalField(max_digits=6, decimal_places=2, default=500.00)
    registration_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.vehicle_type}"

# ==========================================
# 2. PRODUCE & QUALITY GRADING
# ==========================================
class ProduceListing(models.Model):
    CATEGORY_CHOICES = (
        ('GRAINS', 'Grains'),
        ('VEGETABLES', 'Fresh Vegetables'),
        ('TOMATOES', 'Fresh Tomatoes'),
        ('FRUITS', 'Fruits'),
        ('LEGUMES', 'Legumes'),
        ('OTHER', 'Other'),
    )
    STATUS_CHOICES = (
        ('Available', 'Available'),
        ('Sold Out', 'Sold Out'),
        ('In Transit', 'In Transit'),
    )

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'FARMER'})
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='VEGETABLES')
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in Emalangeni (E)")
    available_quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    
    quality_grade = models.CharField(max_length=1, choices=(('A', 'A'), ('B', 'B'), ('C', 'C')), default='B')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    image = models.ImageField(upload_to='produce_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.available_quantity_kg}kg {self.product_name}"

# ==========================================
# 3. ORDERS & ESCROW (ATOMIC CHECKOUT)
# ==========================================
class Order(models.Model):
    ORDER_STATUS = (
        ('Pending', 'Pending Payment'),
        ('IN_ESCROW', 'Funds in Escrow'),
        ('In Transit', 'Out for Delivery'),
        ('Completed', 'Completed'),
        ('DISPUTED', 'Under Dispute'),
    )
    PAYMENT_CHOICES = (
        ('CASH', 'Cash on Delivery'),
        ('MOBILE', 'Mobile Money (MoMo)'),
        ('CARD', 'Credit/Debit Card'),
    )

    buyer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders', limit_choices_to={'role': 'BUYER'})
    matched_driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', limit_choices_to={'role': 'DRIVER'})
    
    total_produce_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transport_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='MOBILE')
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')
    verification_pin = models.CharField(max_length=4, blank=True, null=True)
    
    # Archiving logic
    is_archived_by_buyer = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.total_produce_amount + self.transport_fee
        if not self.verification_pin:
            self.verification_pin = str(random.randint(1000, 9999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.buyer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    produce = models.ForeignKey(ProduceListing, on_delete=models.PROTECT)
    quantity_ordered_kg = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

class EscrowTransaction(models.Model):
    ESCROW_STATUS = (
        ('HELD', 'Funds Held Safely'),
        ('RELEASED', 'Released to Farmers/Drivers'),
        ('DISPUTED', 'Frozen - Admin Mediation Required'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='escrow')
    transaction_reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    amount_held = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ESCROW_STATUS, default='HELD')
    
    dispute_reason = models.TextField(blank=True, null=True)
    admin_resolution_notes = models.TextField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)

class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    target_entity = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class OTPRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

# ==========================================
# 4. RATINGS SYSTEM
# ==========================================
class Rating(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ratings')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'reviewer', 'reviewee')

    def __str__(self):
        return f"{self.reviewer.username} rated {self.reviewee.username}: {self.score} Stars"

# ==========================================
# 5. NEW UPGRADES (PAYMENTS, FULFILMENTS, SETTINGS)
# ==========================================
class PlatformSetting(models.Model):
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Percentage e.g. 10.00")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commission: {self.commission_rate}%"

class PaymentTransaction(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20) # MOMO or CARD
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    reference = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderFulfilment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Awaiting Confirmation'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='fulfilments')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'FARMER'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Fulfilment for Order #{self.order.id} - {self.farmer.username}"