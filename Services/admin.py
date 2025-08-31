from django.contrib import admin
from Services.models import (
    Product, 
    ProductType,
    ProductColor,
    ProductColorSize,
    ProductDesign,
    ProductImage,
)

# ---------------- Inline for nested objects ----------------
class ProductTypeInline(admin.TabularInline):
    model = ProductType
    extra = 1

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

class ProductColorSizeInline(admin.TabularInline):
    model = ProductColorSize
    extra = 1

class ProductDesignInline(admin.TabularInline):
    model = ProductDesign
    extra = 1
    autocomplete_fields = ['type']  # helpful if you have many ProductTypes

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" />'
        return ""
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


# ---------------- Register main models ----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'date_added']
    inlines = [ProductTypeInline, ProductColorInline, ProductImageInline]

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['product', 'type_name', 'price', 'discount_percent', 'discounted_price']
    search_fields = ['type_name', 'product__name']  # <-- REQUIRED for autocomplete_fields

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['product', 'name']
    inlines = [ProductColorSizeInline, ProductDesignInline]

@admin.register(ProductColorSize)
class ProductColorSizeAdmin(admin.ModelAdmin):
    list_display = ['color', 'size', 'quantity']

@admin.register(ProductDesign)
class ProductDesignAdmin(admin.ModelAdmin):
    list_display = ['color', 'name', 'type', 'price', 'discounted_price']
    autocomplete_fields = ['type']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'design', 'image']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" />'
        return ""
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'
