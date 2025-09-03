from django.contrib import admin
from .models import Product, ProductType, ProductColor, ProductColorSize, ProductDesign, ProductImage


# Inline for Product Types
class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1


# Inline for Product Colors
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


# Inline for Product Images (only product-level images)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "color", "design")
    readonly_fields = ()
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "date_added")
    search_fields = ("product_id", "name")
    inlines = [ProductTypeInline, ProductColorInline, ProductImageInline]


# --- Deeper Models ---
class ProductColorSizeInline(admin.TabularInline):
    model = ProductColorSize
    extra = 1


class ProductDesignInline(admin.TabularInline):
    model = ProductDesign
    extra = 1


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("name", "product")
    search_fields = ("name", "product__name")
    inlines = [ProductColorSizeInline, ProductDesignInline]


@admin.register(ProductDesign)
class ProductDesignAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "type")
    search_fields = ("name", "color__name", "type__type_name")
    inlines = [ProductImageInline]  # allow design-specific images


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("product", "type_name", "price", "discount_price", "discount_percent")
    search_fields = ("product__name", "type_name")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "design", "image")
    search_fields = ("product__name", "color__name", "design__name")
