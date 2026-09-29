from django.conf import settings
from django.db import models

from core.models import BaseModel


class Wallet(BaseModel):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="wallet",
    )
    balance = models.DecimalField(max_digits=14, decimal_places=0, default=0)

    def __str__(self):
        return f"Wallet({self.user.phone_number}) = {self.balance}"

    def apply_transaction(self, amount, type_, related_suborder=None, description=""):

        WalletTransaction.objects.create(
            wallet=self,
            amount=amount,
            type=type_,
            related_suborder=related_suborder,
            description=description,
        )
        self.balance = models.F("balance") + amount
        self.save(update_fields=["balance", "updated_at"])
        self.refresh_from_db(fields=["balance"])


class WalletTransaction(BaseModel):

    class Type(models.TextChoices):
        SALE_CREDIT = "sale_credit", "Sale credit"
        COMMISSION_FEE = "commission_fee", "Commission fee"
        WITHDRAWAL = "withdrawal", "Withdrawal"
        REFUND_CREDIT = "refund_credit", "Refund credit"

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=0)
    type = models.CharField(max_length=20, choices=Type.choices)
    related_suborder = models.ForeignKey(
        "orders.SubOrder",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="wallet_transactions",
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} -> {self.wallet}"


class Payment(BaseModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=0)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    reference = models.CharField(
        max_length=40, blank=True, help_text="Fake gateway transaction reference"
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for Order #{self.order_id} ({self.status})"


class WithdrawalRequest(BaseModel):
    """A seller's request to cash out their wallet balance. Approval creates the debiting WalletTransaction."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="withdrawal_requests"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=0)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Withdrawal {self.amount} for {self.wallet.user.phone_number} ({self.status})"

    def approve(self):
        from django.utils import timezone

        if self.status != self.Status.PENDING:
            return
        self.wallet.apply_transaction(
            amount=-self.amount,
            type_=WalletTransaction.Type.WITHDRAWAL,
            description=f"Withdrawal request #{self.id}",
        )
        self.status = self.Status.APPROVED
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_at", "updated_at"])

    def reject(self):
        from django.utils import timezone

        self.status = self.Status.REJECTED
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_at", "updated_at"])
