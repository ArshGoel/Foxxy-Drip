from django.contrib import admin
from .models import (
    Product,
    ProductType,
    ProductColor,
    ProductColorSize,
    ProductDesign,
    ProductImage,
)


# ----------------- Inline Models -----------------
class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


class ProductDesignInline(admin.TabularInline):
    model = ProductDesign
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# ----------------- Main Admin -----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "date_added")
    search_fields = ("product_id", "name")
    inlines = [ProductTypeInline, ProductColorInline, ProductImageInline]


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("product", "type_name", "price", "discount_price")
    list_filter = ("type_name",)
    search_fields = ("product__name",)


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("product", "name")


@admin.register(ProductColorSize)
class ProductColorSizeAdmin(admin.ModelAdmin):
    list_display = ("color", "size", "quantity")


@admin.register(ProductDesign)
class ProductDesignAdmin(admin.ModelAdmin):
    list_display = ("color", "name", "type", "price", "discounted_price")
    search_fields = ("name", "color__name", "type__type_name")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "design", "image")
