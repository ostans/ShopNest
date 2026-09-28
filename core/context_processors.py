from products.models import Category


def site_defaults(request):
    return {
        "site_name": "ShopNest",
        "site_description": "Your one-stop shop for all your needs.",
    }


def categories(request):
    return {
        "categories": Category.objects.filter(parent__isnull=True)
        .prefetch_related("children")
        .order_by("name")
    }
