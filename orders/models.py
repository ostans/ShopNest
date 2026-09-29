from django.conf import settings
from django.db import models

from accounts.models import Address
from core.models import BaseModel
from products.models import Product


class Order(BaseModel):

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    total_price = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    receiver_name = models.CharField(max_length=150)
    receiver_phone = models.CharField(max_length=16)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} ({self.buyer.phone_number})"

    @property
    def is_fully_paid(self):
        return (
            self.sub_orders.exclude(status=SubOrder.STATUS_AWAITING_PAYMENT).exists()
            and not self.sub_orders.filter(
                status=SubOrder.STATUS_AWAITING_PAYMENT
            ).exists()
        )


class SubOrder(BaseModel):

    class Status(models.TextChoices):
        AWAITING_PAYMENT = "awaiting_payment", "Awaiting payment"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="sub_orders"
    )
    store = models.ForeignKey(
        "stores.Store", on_delete=models.PROTECT, related_name="sub_orders"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AWAITING_PAYMENT
    )
    subtotal = models.DecimalField(max_digits=14, decimal_places=0, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SubOrder #{self.id} ({self.store.name})"

    def mark_paid(self):
        self.status = self.Status.PAID
        self.save(update_fields=["status", "updated_at"])

    def mark_completed(self):

        from django.db import transaction
        from payments.services import credit_seller_for_suborder

        with transaction.atomic():
            self.status = self.Status.COMPLETED
            self.save(update_fields=["status", "updated_at"])
            credit_seller_for_suborder(self)

    def mark_cancelled(self, refund=True):

        from django.db import transaction

        with transaction.atomic():
            was_paid = self.status in (self.Status.PAID, self.Status.SHIPPED)
            self.status = self.Status.CANCELLED
            self.save(update_fields=["status", "updated_at"])

            if refund and was_paid:
                from payments.services import credit_buyer_refund

                credit_buyer_refund(
                    self.order.buyer,
                    self.subtotal,
                    sub_order=self,
                    description=f"Refund for cancelled SubOrder #{self.id}",
                )


class OrderItem(BaseModel):

    sub_order = models.ForeignKey(
        SubOrder, on_delete=models.CASCADE, related_name="items"
    )
    listing = models.ForeignKey(
        "stores.Listing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    price_snapshot = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product_name_snapshot}"

    @property
    def line_total(self):
        return self.price_snapshot * self.quantity
