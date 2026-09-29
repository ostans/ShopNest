from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from accounts.models import Address
from cart.models import Cart

from .models import Order, OrderItem, SubOrder


class CheckoutView(LoginRequiredMixin, View):

    template_name = "orders/checkout.html"

    def get(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            messages.info(request, "Your cart is empty.")
            return redirect("cart:detail")

        addresses = request.user.addresses.all()
        return render(
            request,
            self.template_name,
            {
                "cart": cart,
                "groups": cart.items_grouped_by_store(),
                "addresses": addresses,
            },
        )

    def post(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            messages.info(request, "Your cart is empty.")
            return redirect("cart:detail")

        address = get_object_or_404(
            Address, pk=request.POST.get("address_id"), user=request.user
        )

        try:
            order = self._place_order(request.user, address, cart)
        except InsufficientStockError as exc:
            messages.error(request, str(exc))
            return redirect("cart:detail")

        return redirect("orders:pay", pk=order.pk)

    @staticmethod
    @transaction.atomic
    def _place_order(buyer, address, cart):
        from stores.models import Listing

        order = Order.objects.create(
            buyer=buyer,
            receiver_name=address.receiver_name,
            receiver_phone=address.receiver_phone,
            province=address.province,
            city=address.city,
            address_line=address.address_line,
            postal_code=address.postal_code,
        )

        total = 0
        for store, items in cart.items_grouped_by_store().items():
            sub_order = SubOrder.objects.create(order=order, store=store, subtotal=0)
            sub_total = 0

            for item in items:

                listing = Listing.objects.select_for_update().get(pk=item.listing_id)
                if listing.stock_quantity < item.quantity:
                    raise InsufficientStockError(
                        f"Not enough stock for {listing.product.name} (only {listing.stock_quantity} left)."
                    )

                OrderItem.objects.create(
                    sub_order=sub_order,
                    listing=listing,
                    product_name_snapshot=listing.product.name,
                    price_snapshot=listing.price,
                    quantity=item.quantity,
                )
                listing.stock_quantity -= item.quantity
                listing.save(update_fields=["stock_quantity", "updated_at"])
                sub_total += listing.price * item.quantity

            sub_order.subtotal = sub_total
            sub_order.save(update_fields=["subtotal", "updated_at"])
            total += sub_total

        order.total_price = total
        order.save(update_fields=["total_price", "updated_at"])

        cart.items.all().delete()
        return order


class PayOrderView(LoginRequiredMixin, View):

    template_name = "orders/pay.html"

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk, buyer=request.user)
        return render(request, self.template_name, {"order": order})

    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk, buyer=request.user)
        self._process_fake_payment(order)
        messages.success(request, "Payment successful! Your order is being processed.")
        return redirect("order-detail", pk=order.pk)

    @staticmethod
    @transaction.atomic
    def _process_fake_payment(order):
        from django.utils import timezone

        from payments.models import Payment

        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={"amount": order.total_price},
        )
        payment.status = Payment.STATUS_SUCCESS
        payment.reference = f"FAKE-{order.id}-{int(timezone.now().timestamp())}"
        payment.paid_at = timezone.now()
        payment.save()

        for sub_order in order.sub_orders.all():
            sub_order.mark_paid()


class OrderHistoryView(LoginRequiredMixin, ListView):

    model = Order
    template_name = "orders/order_history.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).prefetch_related(
            "sub_orders__items"
        )


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)


class MarkSubOrderReceivedView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        sub_order = get_object_or_404(SubOrder, pk=pk, order__buyer=request.user)
        if sub_order.status == SubOrder.Status.SHIPPED:
            sub_order.mark_completed()
            messages.success(
                request, "Thanks for confirming! The order is marked as completed."
            )
        return redirect("order-detail", pk=sub_order.order_id)
