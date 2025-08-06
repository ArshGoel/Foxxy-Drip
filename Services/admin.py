from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'category', 'price', 'stock', 'date_added')
    list_filter = ('category', 'available_sizes')
    search_fields = ('product_id', 'name', 'category')