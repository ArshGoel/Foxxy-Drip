from django.contrib import admin
from .models import Product, ProductColor, ProductColorSize, ProductDesign, ProductImage

# Inline for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # show 3 empty forms by default
    fields = ['image', 'color', 'design']

# Inline models
class ProductColorSizeInline(admin.TabularInline):
    model = ProductColorSize
    extra = 1

class ProductDesignInline(admin.TabularInline):
    model = ProductDesign
    extra = 1

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    show_change_link = True

# Main admin models
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "product_id", "price", "date_added")
    search_fields = ("name", "product_id")
    inlines = [ProductColorInline, ProductImageInline]

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("name", "product")
    search_fields = ("name", "product__name")
    inlines = [ProductColorSizeInline, ProductDesignInline]

@admin.register(ProductColorSize)
class ProductColorSizeAdmin(admin.ModelAdmin):
    list_display = ("color", "size", "quantity")
    list_filter = ("size",)

@admin.register(ProductDesign)
class ProductDesignAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "get_product")
    search_fields = ("name", "color__name", "color__product__name")
    inlines = [ProductImageInline]

    def get_product(self, obj):
        return obj.color.product
    get_product.short_description = "Product"

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "design")
    search_fields = ("product__name", "color__name", "design__name")
