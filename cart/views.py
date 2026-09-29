from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from .models import Cart, CartItem


class CartDetailView(LoginRequiredMixin, TemplateView):

    template_name = "cart/cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        context["cart"] = cart
        context["groups"] = cart.items_grouped_by_store()
        return context


class AddToCartView(LoginRequiredMixin, View):

    def post(self, request, listing_id, *args, **kwargs):
        from stores.models import Listing

        listing = get_object_or_404(Listing, pk=listing_id, is_active=True)
        quantity = int(request.POST.get("quantity", 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            listing=listing,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity

        item.clean_quantity_against_stock()
        item.save()

        messages.success(request, f"{listing.product.name} added to your cart.")
        return redirect(request.META.get("HTTP_REFERER", "cart-detail"))


class UpdateCartItemView(LoginRequiredMixin, View):

    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1

        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.clean_quantity_against_stock()
            item.save()

        return redirect("cart-detail")


class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        item.delete()
        messages.info(request, "Item removed from cart.")
        return redirect("cart-detail")
