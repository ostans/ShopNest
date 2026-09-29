from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from core.mixins import SellerRequiredMixin, StoreOwnerRequiredMixin
from products.forms import ProductForm
from products.models import Product

from .forms import ListingForm, StoreForm
from .models import Listing, Store


class StoreCreateView(SellerRequiredMixin, CreateView):

    model = Store
    form_class = StoreForm
    template_name = "stores/store_create.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("seller-dashboard")


class StoreListingsView(StoreOwnerRequiredMixin, ListView):

    model = Listing
    template_name = "stores/store_listings.html"
    context_object_name = "listings"

    def get_queryset(self):
        return (
            Listing.objects.filter(store=self.store)
            .select_related("product")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = self.store
        return context


class ListingSearchProductView(StoreOwnerRequiredMixin, TemplateView):

    template_name = "stores/listing_search_product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = self.store
        query = self.request.GET.get("q", "").strip()
        context["query"] = query

        results = Product.objects.none()
        if query:
            results = Product.objects.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            ).exclude(listings__store=self.store)

        context["results"] = results
        return context


class ProductQuickCreateView(StoreOwnerRequiredMixin, CreateView):

    model = Product
    form_class = ProductForm
    template_name = "stores/product_quick_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = self.store
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        Product.objects.create(**form.cleaned_data)
        messages.success(
            self.request, "Product created. You can now set a price for it."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "listing-create",
            kwargs={
                "store_slug": self.store.slug,
                "product_id": self.object.id,
            },
        )


class ListingCreateView(StoreOwnerRequiredMixin, CreateView):

    model = Listing
    form_class = ListingForm
    template_name = "stores/listing_form.html"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.product = get_object_or_404(Product, pk=self.kwargs["product_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = self.store
        context["product"] = self.product
        return context

    def form_valid(self, form):
        if Listing.objects.filter(store=self.store, product=self.product).exists():
            messages.error(
                self.request, "This store already has a listing for that product."
            )
            return redirect("listings", store_slug=self.store.slug)

        form.instance.store = self.store
        form.instance.product = self.product
        messages.success(self.request, "Listing created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("listings", kwargs={"store_slug": self.store.slug})


class ListingUpdateView(StoreOwnerRequiredMixin, UpdateView):
    model = Listing
    form_class = ListingForm
    template_name = "stores/listing_form.html"

    def get_queryset(self):
        return Listing.objects.filter(store=self.store)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = self.store
        context["product"] = self.object.product
        return context

    def form_valid(self, form):
        messages.success(self.request, "Listing updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("listings", kwargs={"store_slug": self.store.slug})


class ListingDeleteView(StoreOwnerRequiredMixin, DeleteView):
    model = Listing
    template_name = "stores/listing_confirm_delete.html"

    def get_queryset(self):
        return Listing.objects.filter(store=self.store)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = self.store
        return context

    def form_valid(self, form):
        messages.info(self.request, "Listing removed.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("listings", kwargs={"store_slug": self.store.slug})


class SellerProfileEditView(SellerRequiredMixin, UpdateView):

    template_name = "stores/seller_profile_form.html"

    def get_object(self, queryset=None):
        return self.request.user.seller_profile

    def get_form_class(self):
        from accounts.forms import EditSellerProfileForm

        return EditSellerProfileForm

    def form_valid(self, form):
        messages.success(self.request, "Your seller profile has been updated.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("seller-dashboard")


class StoreOrdersView(StoreOwnerRequiredMixin, ListView):

    template_name = "stores/store_orders.html"
    context_object_name = "sub_orders"
    paginate_by = 20

    def get_queryset(self):
        from orders.models import SubOrder

        return (
            SubOrder.objects.filter(store=self.store)
            .select_related("order")
            .prefetch_related("items")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["store"] = self.store
        return context


class MarkSubOrderShippedView(StoreOwnerRequiredMixin, View):

    def post(self, request, store_slug, pk, *args, **kwargs):
        from orders.models import SubOrder

        sub_order = get_object_or_404(SubOrder, pk=pk, store=self.store)
        if sub_order.status == SubOrder.Status.PAID:
            sub_order.status = SubOrder.Status.SHIPPED
            sub_order.save(update_fields=["status", "updated_at"])
            messages.success(request, f"SubOrder #{sub_order.id} marked as shipped.")
        return redirect("orders", store_slug=self.store.slug)
