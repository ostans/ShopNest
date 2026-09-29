from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Order, OrderItem, SubOrder


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["listing", "product__name", "price_snapshot", "quantity"]


class SubOrderInline(admin.TabularInline):
    model = SubOrder
    extra = 0
    readonly_fields = ["store", "status", "subtotal"]
    show_change_link = True


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["id", "buyer", "total_price", "created_at"]
    search_fields = ["buyer__phone_number", "receiver_name"]
    inlines = [SubOrderInline]


@admin.register(SubOrder)
class SubOrderAdmin(ModelAdmin):
    list_display = ["id", "order", "store", "status", "subtotal", "created_at"]
    list_filter = ["status"]
    search_fields = ["store__name", "order__buyer__phone_number"]
    inlines = [OrderItemInline]
    actions = ["mark_shipped", "mark_completed"]

    @admin.action(description="Mark selected as shipped")
    def mark_shipped(self, request, queryset):
        for sub_order in queryset.filter(status=SubOrder.Status.PAID):
            sub_order.status = SubOrder.Status.SHIPPED
            sub_order.save(update_fields=["status"])

    @admin.action(description="Mark selected as completed (credits seller wallet)")
    def mark_completed(self, request, queryset):
        for sub_order in queryset.filter(status=SubOrder.Status.SHIPPED):
            sub_order.mark_completed()
