from django.conf import settings
from django.db import models

from core.models import BaseModel
from stores.models import Listing


class Cart(BaseModel):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    class Meta:
        verbose_name = "cart"
        verbose_name_plural = "carts"

    def __str__(self):
        return f"Cart({self.user.phone_number})"

    @property
    def total_price(self):
        return sum(
            (item.subtotal for item in self.items.select_related("listing")), start=0
        )

    @property
    def total_items(self):
        return sum(self.items.values_list("quantity", flat=True))

    def items_grouped_by_store(self):
        groups = {}
        for item in self.items.select_related(
            "listing", "listing__store", "listing__product"
        ):
            groups.setdefault(item.listing.store, []).append(item)
        return groups


class CartItem(BaseModel):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "cart item"
        verbose_name_plural = "cart items"
        unique_together = [
            "cart",
            "listing",
        ]

    def __str__(self):
        return f"{self.quantity} x {self.listing} (cart #{self.cart_id})"

    @property
    def subtotal(self):
        return self.listing.price * self.quantity

    def clean_quantity_against_stock(self):
        if self.quantity > self.listing.stock_quantity:
            self.quantity = max(self.listing.stock_quantity, 0)
