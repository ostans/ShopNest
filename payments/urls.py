from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("", views.WalletDetailView.as_view(), name="wallet"),
    path("withdraw/", views.WithdrawalRequestView.as_view(), name="withdraw"),
]
