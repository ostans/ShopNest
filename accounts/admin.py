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
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    filter_horizontal = ["groups", "user_permissions"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(ModelAdmin):
    ordering = ["-created_at"]
    list_display = ["user_full_name", "user__phone_number"]
    search_fields = [
        "user__phone_number",
        "user__first_name",
        "user__last_name",
    ]

    @admin.display(description="User")
    def user_full_name(self, obj):
        return obj.user.full_name if obj.user else ""


@admin.register(SellerProfile)
class SellerProfileAdmin(ModelAdmin):
    ordering = ["-created_at"]
    list_display = [
        "user_full_name",
        "user__phone_number",
    ]
    search_fields = [
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "national_id",
    ]

    @admin.display(description="User")
    def user_full_name(self, obj):
        return obj.user.full_name if obj.user else ""
