import os
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.deconstruct import deconstructible


# ----------------- Image path generator -----------------
@deconstructible
class ProductImagePath:
    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        timestamp = int(now().timestamp())

        # Determine base name depending on what the image belongs to
        if hasattr(instance, "design") and instance.design:
            # If image belongs to a design
            base_name = f"{instance.design.color.product.product_id}_design_{instance.design.id}_{timestamp}"
        elif hasattr(instance, "color") and instance.color:
            # If image belongs to a color
            base_name = f"{instance.color.product.product_id}_color_{instance.color.id}_{timestamp}"
        elif hasattr(instance, "product") and instance.product:
            # If image belongs to the product itself
            base_name = f"{instance.product.product_id}_product_{timestamp}"
        else:
            # fallback
            base_name = f"product_{timestamp}"

        # final path
        return os.path.join("products", f"{base_name}.{ext}")


# ----------------- Product -----------------
class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)  # type:ignore
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.product_id})"

    def save(self, *args, **kwargs):
        if not self.product_id:
            existing_ids = Product.objects.values_list("product_id", flat=True)
            existing_nums = sorted([int(pid[1:]) for pid in existing_ids if pid[1:].isdigit()])
            next_id = 1
            for num in existing_nums:
                if num == next_id:
                    next_id += 1
                else:
                    break
            self.product_id = f"P{next_id:03}"
        super().save(*args, **kwargs)
    @property
    def size_stock(self):
        """
        Returns a dictionary:
        { 'Color Name': { 'S': qty, 'M': qty, ... }, ... }
        """
        data = {}
        for color in self.colors.all(): # type: ignore
            data[color.name] = {size_obj.size: size_obj.quantity for size_obj in color.sizes.all()}
        return data


# ----------------- ProductColor -----------------
class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# ----------------- ProductColorSize -----------------
class ProductColorSize(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large")
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

    def __str__(self):
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