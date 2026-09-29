from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from core.mixins import SellerRequiredMixin

from .models import Wallet, WithdrawalRequest


class WalletDetailView(LoginRequiredMixin, View):

    template_name = "payments/wallet_detail.html"

    def get(self, request, *args, **kwargs):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        transactions = wallet.transactions.all()[:50]
        return render(
            request,
            self.template_name,
            {"wallet": wallet, "transactions": transactions},
        )


class WithdrawalRequestView(SellerRequiredMixin, FormView):

    template_name = "payments/withdrawal_form.html"
    success_url = reverse_lazy("payments:wallet")

    def get_form(self, form_class=None):
        from django import forms

        class WithdrawalForm(forms.Form):
            amount = forms.DecimalField(
                max_digits=14,
                decimal_places=0,
                min_value=1,
                widget=forms.NumberInput(attrs={"class": "form-control"}),
            )

        return WithdrawalForm(**self.get_form_kwargs())

    def form_valid(self, form):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        amount = form.cleaned_data["amount"]

        if amount > wallet.balance:
            form.add_error("amount", "Amount exceeds your wallet balance.")
            return self.form_invalid(form)

        WithdrawalRequest.objects.create(wallet=wallet, amount=amount)
        messages.success(self.request, "Withdrawal request submitted for admin review.")
        return super().form_valid(form)
