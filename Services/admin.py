from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .models import (
    Product,
    ProductType,
    ProductColor,
    ProductColorSize,
    ProductDesign,
    ProductImage
)

# -----------------------------------------
# Utility function to compress images
def compress_image(image_file, max_size=5242880):
    """
    Compress image to reduce file size while maintaining quality.
    Target: Under 5MB
    """
    try:
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Resize if too large (max 2000px width)
        max_width = 2000
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Compress with quality reduction
        output = BytesIO()
        quality = 85
        
        # Iteratively reduce quality until under size limit
        while quality > 30:
            output.seek(0)
            output.truncate(0)
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            if output.tell() <= max_size:
                break
            quality -= 5
        
        output.seek(0)
        
        # Return compressed image with original filename
        filename = image_file.name
        if not filename.lower().endswith('.jpg') and not filename.lower().endswith('.jpeg'):
            filename = filename.rsplit('.', 1)[0] + '.jpg'
        
        return ContentFile(output.getvalue(), name=filename)
    
    except Exception as e:
        print(f"Image compression error: {e}")
        return image_file


# -----------------------------------------
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
    max_num = 1  # Only 1 image per inline to stay under 6MB
    
    def save_formset(self, request, form, formset, change):
        """Compress and validate image before saving"""
        for form in formset.forms:
            if form.cleaned_data.get('image'):
                image = form.cleaned_data['image']
                
                # Compress if too large
                if image.size > 5242880:  # 5MB limit
                    image = compress_image(image)
                    form.cleaned_data['image'] = image
                    form.instance.image = image
        
        super().save_formset(request, form, formset, change)


# Inline for ProductImage used in ProductDesignAdmin
class ProductImageDesignInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "color", "design")  # Exclude 'product' to avoid issues
    max_num = 1  # Only 1 image per inline to stay under 6MB
    
    def save_formset(self, request, form, formset, change):
        """Compress and validate image before saving"""
        for form in formset.forms:
            if form.cleaned_data.get('image'):
                image = form.cleaned_data['image']
                
                # Compress if too large
                if image.size > 5242880:  # 5MB limit
                    image = compress_image(image)
                    form.cleaned_data['image'] = image
                    form.instance.image = image
        
        super().save_formset(request, form, formset, change)


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
