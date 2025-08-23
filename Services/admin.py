from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "category", "price", "color", "date_added")
    list_filter = ("category", "date_added")
    search_fields = ("name", "product_id", "color")
    ordering = ("-date_added",)

    # Group fields into sections
    fieldsets = (
        ("Basic Info", {
            "fields": ("product_id", "name", "description", "category", "price", "color", "image")
        }),
        ("Stock by Size", {
            "fields": (
                "qty_xxs", "qty_xs", "qty_s", "qty_m", 
                "qty_l", "qty_xl", "qty_xxl", "qty_xxxl"
            ),
        }),
        ("Metadata", {
            "fields": ("date_added",),
        }),
    )

    readonly_fields = ("date_added",)  # auto-filled