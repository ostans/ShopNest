from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['listing', 'quantity']


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'updated_at']
    search_fields = ['user__phone_number']
    inlines = [CartItemInline]
