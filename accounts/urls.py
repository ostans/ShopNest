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
]
