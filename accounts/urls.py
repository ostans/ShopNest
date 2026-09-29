from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.customer_register_view, name="register"),
    path("dashboard/", views.customer_dashboard_view, name="customer-dashboard"),
    path("become-seller/", views.become_seller_view, name="become-seller"),
    path("seller/register/", views.seller_register_view, name="seller-register"),
    path("seller/dashboard/", views.seller_dashboard_view, name="seller-dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("addresses/", views.address_list_view, name="address-list"),
    path("addresses/new/", views.address_create_view, name="address-create"),
    path("addresses/<int:pk>/edit/", views.address_update_view, name="address-update"),
    path(
        "addresses/<int:pk>/delete/", views.address_delete_view, name="address-delete"
    ),
]
