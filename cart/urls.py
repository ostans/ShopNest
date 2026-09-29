from django.urls import path

from . import views

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="cart-detail"),
    path("add/<int:listing_id>/", views.AddToCartView.as_view(), name="add-to-cart"),
    path(
        "item/<int:item_id>/update/",
        views.UpdateCartItemView.as_view(),
        name="update-item",
    ),
    path(
        "item/<int:item_id>/remove/",
        views.RemoveFromCartView.as_view(),
        name="remove-item",
    ),
]
