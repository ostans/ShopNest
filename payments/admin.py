from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Payment, Wallet, WalletTransaction, WithdrawalRequest


class WalletTransactionInline(admin.TabularInline):
    model = WalletTransaction
    extra = 0
    readonly_fields = [
        "amount",
        "type",
        "related_suborder",
        "description",
        "created_at",
    ]
    can_delete = False


@admin.register(Wallet)
class WalletAdmin(ModelAdmin):
    list_display = ["user", "balance", "updated_at"]
    search_fields = ["user__phone_number"]
    inlines = [WalletTransactionInline]


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ["order", "amount", "status", "paid_at"]
    list_filter = ["status"]


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ["wallet", "amount", "status", "created_at", "reviewed_at"]
    list_filter = ["status"]
    actions = ["approve_selected", "reject_selected"]

    @admin.action(description="Approve selected withdrawal requests")
    def approve_selected(self, request, queryset):
        for wr in queryset.filter(status=WithdrawalRequest.Status.PENDING):
            wr.approve()

    @admin.action(description="Reject selected withdrawal requests")
    def reject_selected(self, request, queryset):
        for wr in queryset.filter(status=WithdrawalRequest.Status.PENDING):
            wr.reject()
