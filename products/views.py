from django.db.models import Min, Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Hero, Product

PAGE_SIZE = 12


class ProductListMixin:

    model = Product
    paginate_by = PAGE_SIZE
    context_object_name = "products"

    def base_queryset(self):
        return (
            Product.objects.annotate(
                min_price=Min("listings__price", filter=self._active_listing_filter())
            )
            .filter(min_price__isnull=False)
            .select_related("category")
            .prefetch_related("images")
        )

    @staticmethod
    def _active_listing_filter():
        return Q(listings__is_active=True, listings__stock_quantity__gt=0)


class HomeView(ProductListMixin, ListView):
    template_name = "products/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["heroes"] = Hero.objects.filter(is_active=True).order_by("id")
        context["categories"] = Category.objects.prefetch_related("children").filter(
            parent__isnull=True
        )
        context["products"] = self.base_queryset().order_by("created_at")
        return context


class CategoryProductListView(ProductListMixin, ListView):
    template_name = "products/category_list.html"

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return (
            Product.objects.annotate(
                min_price=Min("listings__price", filter=self._active_listing_filter())
            )
            .filter(category=self.category)
            .order_by("created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProductSearchView(ProductListMixin, ListView):
    template_name = "products/search_results.html"

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()

        if not self.query:
            return self.base_queryset().none()

        return self.base_queryset().filter(
            Q(name__icontains=self.query)
            | Q(description__icontains=self.query)
            | Q(category__name__icontains=self.query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        return context


class ProductDetailView(DetailView):

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.prefetch_related("images")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listings = (
            self.object.listings.filter(is_active=True)
            .select_related("store")
            .order_by("price")
        )
        context["listings"] = listings
        context["lowest_listing_price"] = (
            listings.filter(stock_quantity__gt=0)
            .values_list("price", flat=True)
            .first()
        )
        return context
