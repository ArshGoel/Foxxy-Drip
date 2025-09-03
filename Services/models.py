from decimal import Decimal
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.deconstruct import deconstructible
import os


# ----------------- Image path generator -----------------
@deconstructible
class ProductImagePath:
    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        timestamp = int(now().timestamp())

        if hasattr(instance, "design") and instance.design:
            base_name = f"{instance.design.color.product.product_id}_design_{instance.design.id}_{timestamp}"
        elif hasattr(instance, "color") and instance.color:
            base_name = f"{instance.color.product.product_id}_color_{instance.color.id}_{timestamp}"
        elif hasattr(instance, "product") and instance.product:
            base_name = f"{instance.product.product_id}_product_{timestamp}"
        else:
            base_name = f"product_{timestamp}"

        return os.path.join("products", f"{base_name}.{ext}")


# ----------------- Product -----------------
class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.product_id})"


# ----------------- ProductType -----------------
class ProductType(models.Model):
    TYPE_CHOICES = [
        ("plain", "Plain"),
        ("printed", "Printed"),
        ("embroidery", "Embroidery"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="types")
    type_name = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)#type:ignore
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, blank=True, null=True) #type:ignore

    @property
    def discounted_price(self):
        """If discount_price is set, return it, else return original price"""
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def discount_percent(self):
        """Calculate % off automatically"""
        if self.discount_price and self.discount_price < self.price:
            return round(100 - (self.discount_price / self.price * 100))
        return 0

    def __str__(self):
        return f"{self.product.name} - {self.type_name}"


# ----------------- ProductColor -----------------
class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# ----------------- ProductColorSize -----------------
class ProductColorSize(models.Model):
    SIZE_CHOICES = [
        ("XXS", "Extra Extra Small"),
        ("XS", "Extra Small"),
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
        ("XXL", "Extra Extra Large"),
        ("XXXL", "Extra Extra Extra Large")
    ]
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name="sizes")
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.color.name} - {self.size} ({self.quantity})"


# ----------------- ProductDesign -----------------
class ProductDesign(models.Model):
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name="designs")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        related_name="designs",
        null=True,
        blank=True
    )

    @property
    def price(self):
        return self.type.price if self.type else 0

    @property
    def discounted_price(self):
        return self.type.discount_price if self.type else 0

    def __str__(self):
        if self.type:
            return f"{self.color.name} - {self.name} ({self.type.type_name})"
        return f"{self.color.name} - {self.name}"


# ----------------- ProductImage -----------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    color = models.ForeignKey(ProductColor, related_name="images", on_delete=models.CASCADE, blank=True, null=True)
    design = models.ForeignKey(ProductDesign, related_name="images", on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to=ProductImagePath())

    def __str__(self):
        parts = [self.product.name]
        if self.color:
            parts.append(self.color.name)
        if self.design:
            parts.append(self.design.name)
        return " - ".join(parts)


# ----------------- Auto-delete image files -----------------
@receiver(post_delete, sender=ProductImage)
def delete_extra_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
