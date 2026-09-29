from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from core.models import BaseModel

phone_regex = RegexValidator(
    regex=r"^\+989\d{9}$",
    message="Phone number must be in the format: +989XXXXXXXXX",
)


class CustomUserManager(BaseUserManager):

    def _create_user(self, phone_number, password=None, **extra_fields):
        first_name = extra_fields.get("first_name")
        last_name = extra_fields.get("last_name")
        if not phone_number:
            raise ValueError("The Phone Number field must be set")
        if not first_name or not last_name:
            raise ValueError("The Fullname fiel must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        SELLER = "seller", "Seller"
        STAFF = "staff", "Staff"

    phone_number = models.CharField(
        max_length=13, unique=True, validators=[phone_regex]
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=11, choices=Role.choices, default=Role.CUSTOMER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"


class CustomerProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    avatar = models.ImageField(upload_to="customers/avatars/", blank=True, null=True)

    def __str__(self):
        return f"Customer Profile - {self.user.full_name}"


class SellerProfile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_profile",
    )
    national_id = models.CharField(max_length=10, unique=True)
    logo = models.ImageField(upload_to="sellers/logos/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Seller Profile - {self.user.full_name}"


class Address(BaseModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    receiver_name = models.CharField(
        max_length=150, help_text="Name of the person receiving the package"
    )
    receiver_phone = models.CharField(max_length=16, validators=[phone_regex])
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "address"
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.receiver_name} - {self.city}, {self.address_line[:30]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(
                is_default=False
            )
        elif not Address.objects.filter(user=self.user, is_default=True).exists():
            Address.objects.filter(pk=self.pk).update(is_default=True)
