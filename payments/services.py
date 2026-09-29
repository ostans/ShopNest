from decimal import Decimal

from django.conf import settings


def credit_seller_for_suborder(sub_order):

    from .models import Wallet, WalletTransaction

    seller_user = sub_order.store.owner
    wallet, _ = Wallet.objects.get_or_create(user=seller_user)

    commission_rate = Decimal(str(getattr(settings, "PLATFORM_COMMISSION_RATE", 0)))
    commission = (sub_order.subtotal * commission_rate).quantize(Decimal("1"))
    net_amount = sub_order.subtotal - commission

    wallet.apply_transaction(
        amount=net_amount,
        type_=WalletTransaction.Type.SALE_CREDIT,
        related_suborder=sub_order,
        description=f"Sale for SubOrder #{sub_order.id} (commission {commission} deducted)",
    )


def credit_buyer_refund(user, amount, sub_order=None, description=""):

    from .models import Wallet, WalletTransaction

    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.apply_transaction(
        amount=amount,
        type_=WalletTransaction.Type.REFUND_CREDIT,
        related_suborder=sub_order,
        description=(
            description or f"Refund for SubOrder #{sub_order.id}"
            if sub_order
            else description
        ),
    )
