from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import (
    Product,
    ProductType,
    ProductColor,
    ProductColorSize,
    ProductDesign,
    ProductImage
)

# -----------------------------------------
# Inline for ProductType
class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1


# Inline for ProductColor
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


# Inline for ProductColorSize
class ProductColorSizeInline(admin.TabularInline):
    model = ProductColorSize
    extra = 1


# Inline for ProductDesign
class ProductDesignInline(admin.TabularInline):
    model = ProductDesign
    extra = 1


# Inline for ProductImage used in ProductAdmin
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "color", "design")
    readonly_fields = ()
    show_change_link = True


# Inline for ProductImage used in ProductDesignAdmin
class ProductImageDesignInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "color", "design")  # Exclude 'product' to avoid issues


# -----------------------------------------
# Admin for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_id", "name", "date_added")
    search_fields = ("product_id", "name")
    inlines = [ProductTypeInline, ProductColorInline, ProductImageInline]


# Admin for ProductColor
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("name", "product")
    search_fields = ("name", "product__name")
    inlines = [ProductColorSizeInline, ProductDesignInline]


# Admin for ProductDesign
@admin.register(ProductDesign)
class ProductDesignAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "type")
    search_fields = ("name", "color__name", "type__type_name")


# Admin for ProductType
@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("product", "type_name", "price", "discount_price", "discount_percent")
    search_fields = ("product__name", "type_name")


# Admin for ProductImage
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "design", "image")
    search_fields = ("product__name", "color__name", "design__name")


# -----------------------------------------
# Signal to set product before saving ProductImage
@receiver(pre_save, sender=ProductImage)
def set_product_before_save(sender, instance, **kwargs):
    if not instance.product and instance.design:
        instance.product = instance.design.color.product
