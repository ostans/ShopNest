from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Listing, Store


class ListingInline(admin.TabularInline):
    model = Listing
    extra = 0
    fields = ["product", "price", "stock_quantity", "is_active"]


@admin.register(Store)
class StoreAdmin(ModelAdmin):
    list_display = ["name", "owner", "created_at"]
    search_fields = ["name", "owner__user__phone_number"]
    inlines = [ListingInline]


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ["product", "store", "price", "stock_quantity", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["product__name", "store__name"]
