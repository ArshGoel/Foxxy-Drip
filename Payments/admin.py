from django.contrib import admin
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "merchant_order_id",
        "phonepe_order_id",
        "user",
        "amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("merchant_order_id", "phonepe_order_id", "user__username")
    ordering = ("-created_at",)

    readonly_fields = (
        "merchant_order_id",
        "phonepe_order_id",
        "user",
        "amount",
        "created_at",
    )

    fieldsets = (
        ("Transaction Info", {
            "fields": (
                "merchant_order_id",
                "phonepe_order_id",
                "status",
            )
        }),
        ("User & Amount", {
            "fields": (
                "user",
                "amount",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )
