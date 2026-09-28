from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.ProductSearchView.as_view(), name="search"),
    path(
        "category/<slug:slug>/",
        views.CategoryProductListView.as_view(),
        name="category",
    ),
    path(
        "product/<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"
    ),
]
