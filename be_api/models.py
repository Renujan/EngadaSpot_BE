from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Custom User
from django.contrib.auth.models import AbstractUser
from django.db import models

# be_api/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")  # 👈 force superuser to be admin

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("cashier", "Cashier"),
        ("staff", "Staff"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="staff")

    objects = CustomUserManager()




    # Add related_name to fix reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

# Product
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Beverages','Beverages'),
        ('Snacks','Snacks'),
        ('Main Dishes','Main Dishes'),
        ('Rice','Rice'),
        ('Desserts','Desserts')
    ]
    
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='each')
    stock_type = models.CharField(max_length=20, choices=[('daily_stock','Daily Stock'),('on_demand','On Demand')])
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    total_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# Daily Stock
# models.py
class DailyStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_date = models.DateField()
    starting_stock = models.PositiveIntegerField(default=0)
    added_stock = models.PositiveIntegerField(default=0)
    sold_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)  # new field

    @property
    def remaining_stock(self):
        return self.starting_stock + self.added_stock - self.sold_quantity



# Bill
class Bill(models.Model):
    PAYMENT_CHOICES = [('cash','Cash'),('card','Visa/Card')]
    SECTION_CHOICES = [('customer','Customer'),('kitchen','Kitchen'),('stock','Stock')]

    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='customer')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')

# Bill Item
class BillItem(models.Model):
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Employee Consumption
class EmployeeConsumption(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)

# Printer Settings
class PrinterSetting(models.Model):
    section = models.CharField(max_length=20, choices=Bill.SECTION_CHOICES)
    printer_name = models.CharField(max_length=255)

# Business Info
class BusinessInfo(models.Model):
    logo = models.ImageField(upload_to='business/', null=True, blank=True)
    name = models.CharField(max_length=255, default='SPOT')
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField()
