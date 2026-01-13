from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductType,
    ProductColor,
    ProductColorSize,
    ProductImage,
)

# ------------------ Inline Admins ------------------

class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductColorSizeInline(admin.TabularInline):
    model = ProductColorSize
    extra = 1


# ------------------ Model Admins ------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "category")
    list_filter = ("category",)
    search_fields = ("product_id", "name")
    inlines = [
        ProductTypeInline,
        ProductColorInline,
        ProductImageInline,
    ]


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "type_name",
        "price",
        "discount_price",
        "final_price",
    )
    list_filter = ("type_name",)
    search_fields = ("product__name",)


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("product", "name")
    search_fields = ("product__name", "name")
    inlines = [ProductColorSizeInline]


@admin.register(ProductColorSize)
class ProductColorSizeAdmin(admin.ModelAdmin):
    list_display = ("color", "size", "quantity")
    list_filter = ("size",)
    search_fields = ("color__product__name", "color__name")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "product_type",
        "color",
        "is_primary",
    )
    list_filter = ("is_primary",)
    search_fields = ("product__name",)
