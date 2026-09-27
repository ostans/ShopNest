from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CustomerProfile, SellerProfile, User


@admin.register(User)
class UserAdmin(ModelAdmin):
    ordering = ["-date_joined"]
    list_display = ["phone_number", "first_name", "last_name", "role", "is_staff"]
    search_fields = ["phone_number", "first_name", "last_name"]

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "first_name", "last_name", "role", "password1", "password2"),
            },
        ),
    )
    filter_horizontal = ["groups", "user_permissions"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(ModelAdmin):
    ordering = ["-created_at"]
    list_display = ["user__full_name", "address", "balance"]
    search_fields = ["user__full_name", "address"]
    list_filter = ["balance"]


class SellerProfileAdmin(ModelAdmin):
    ordering = ["-created_at"]
    list_display = ["user__full_name", "national_id", "address", "balance"]
    search_fields = ["user__phone_number", "user__full_name", "national_id"]
    list_filter = ["balance"]
