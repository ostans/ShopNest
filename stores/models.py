from autoslug import AutoSlugField
from django.conf import settings
from django.db import models

from core.models import BaseModel
from products.models import Product


class Store(BaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stores"
    )
    name = models.CharField(max_length=255, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=False)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="store/logos/", blank=True, null=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"{self.name} - {self.owner}"


class Listing(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="listings"
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="listings")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "store")
        ordering = ["price"]

    def __str__(self):
        return f"{self.product.name} @ {self.store.name} ({self.price})"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0 and self.is_active
