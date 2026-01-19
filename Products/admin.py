from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductType,
    ProductColor,
    ProductColorSize,
    Design,          # ✅ NEW
    ProductImage,
)

# ------------------ Inline Admins ------------------

class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


class ProductColorSizeInline(admin.TabularInline):
    model = ProductColorSize
    extra = 1


# ✅ NEW: Design Inline
class DesignInline(admin.TabularInline):
    model = Design
    extra = 1


# ✅ UPDATED: ProductImage Inline (now based on design)
class ProductImageInline(admin.TabularInline):
    model = ProductImage
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

    # ❌ ProductImageInline removed because ProductImage no longer has product FK directly
    inlines = [
        ProductTypeInline,
        ProductColorInline,
        DesignInline,   # ✅ added
    ]


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("product", "type_name", "price", "discount_price", "discounted_price")
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


# ✅ NEW: Design Admin
@admin.register(Design)
class DesignAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "product_type", "color", "show_in_shop")
    list_filter = ("show_in_shop", "product_type")
    search_fields = ("name", "product__name", "color__name")
    inlines = [ProductImageInline]  # ✅ images inside design


# ✅ UPDATED: ProductImage Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "design",
        "is_primary",
    )
    list_filter = ("is_primary",)
    search_fields = ("design__name", "design__product__name")
