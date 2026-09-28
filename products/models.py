from autoslug import AutoSlugField
from django.conf import settings
from django.db import models

from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="name", unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def lowest_price(self):
        listing = self.listings.filter(is_active=True).order_by("price").first()
        return listing.price if listing else None


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "created_at"]

    def __str__(self):
        return f"Image for {self.product.name}"


class Hero(BaseModel):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)

    image = models.ImageField(upload_to="hero/")

    button_text = models.CharField(max_length=50, default="Shop Now")

    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="heroes"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "heroes"

    def __str__(self):
        return self.title
