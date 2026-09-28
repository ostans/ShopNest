from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Category, Hero, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "parent"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["name", "category", "created_by", "created_at"]
    list_filter = ["category"]
    search_fields = ["name"]
    inlines = [ProductImageInline]


@admin.register(Hero)
class HeroAdmin(ModelAdmin):
    list_display = ["title", "product"]
