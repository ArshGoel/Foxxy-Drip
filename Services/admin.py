# admin.py
from django.contrib import admin
from .models import Product, ProductSize

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "category", "price", "date_added")
    search_fields = ("name", "category")
    list_filter = ("category", "date_added")
    inlines = [ProductSizeInline]



