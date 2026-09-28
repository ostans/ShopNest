from django.urls import path

from . import views

urlpatterns = [
    path("stores/new/", views.StoreCreateView.as_view(), name="store-create"),
    path(
        "seller_profile/edit/",
        views.SellerProfileEditView.as_view(),
        name="seller-profile-edit",
    ),
    path(
        "stores/<slug:store_slug>/", views.StoreListingsView.as_view(), name="listings"
    ),
    path(
        "stores/<slug:store_slug>/orders/",
        views.StoreOrdersView.as_view(),
        name="orders",
    ),
    path(
        "stores/<slug:store_slug>/orders/<int:pk>/ship/",
        views.MarkSubOrderShippedView.as_view(),
        name="mark-shipped",
    ),
    path(
        "stores/<slug:store_slug>/listings/add/",
        views.ListingSearchProductView.as_view(),
        name="listing-search",
    ),
    path(
        "stores/<slug:store_slug>/listings/add/new-product/",
        views.ProductQuickCreateView.as_view(),
        name="product-quick-create",
    ),
    path(
        "stores/<slug:store_slug>/listings/add/<int:product_id>/",
        views.ListingCreateView.as_view(),
        name="listing-create",
    ),
    path(
        "stores/<slug:store_slug>/listings/<int:pk>/edit/",
        views.ListingUpdateView.as_view(),
        name="listing-update",
    ),
    path(
        "stores/<slug:store_slug>/listings/<int:pk>/delete/",
        views.ListingDeleteView.as_view(),
        name="listing-delete",
    ),
]
