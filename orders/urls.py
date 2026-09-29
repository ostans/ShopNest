from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("<int:pk>/pay/", views.PayOrderView.as_view(), name="pay"),
    path("", views.OrderHistoryView.as_view(), name="history"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path(
        "sub-order/<int:pk>/mark-received/",
        views.MarkSubOrderReceivedView.as_view(),
        name="mark-received",
    ),
]
