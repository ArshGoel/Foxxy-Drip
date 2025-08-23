import os
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.deconstruct import deconstructible

@deconstructible
class ProductImagePath:
    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # Add timestamp to avoid overwrite & browser cache issues
        filename = f"{instance.product_id}_{int(now().timestamp())}.{ext}"
        return os.path.join('products', filename)


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Tshirt', 'T-shirt'),
        ('Acid Wash T-Shirt', 'Acid Wash T-Shirt'),
        ('Hoodie', 'Hoodie'),
    ]

    product_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    color = models.CharField(max_length=30)
    image = models.ImageField(upload_to=ProductImagePath())
    date_added = models.DateTimeField(auto_now_add=True)

    # 🔹 Quantity for each size
    qty_xxs = models.PositiveIntegerField(default=0)
    qty_xs = models.PositiveIntegerField(default=0)
    qty_s = models.PositiveIntegerField(default=0)
    qty_m = models.PositiveIntegerField(default=0)
    qty_l = models.PositiveIntegerField(default=0)
    qty_xl = models.PositiveIntegerField(default=0)
    qty_xxl = models.PositiveIntegerField(default=0)
    qty_xxxl = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.product_id:
            existing_ids = Product.objects.values_list('product_id', flat=True)
            existing_nums = sorted(
                [int(pid[1:]) for pid in existing_ids if pid[1:].isdigit()]
            )
            
            next_id = 1
            for num in existing_nums:
                if num == next_id:
                    next_id += 1
                else:
                    break
            
            self.product_id = f"P{next_id:03}"

        # delete old image if replacing or clearing
        try:
            this = Product.objects.get(product_id=self.product_id)
            if this.image and (not self.image or this.image != self.image):
                this.image.delete(save=False)
        except Product.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    # 🔹 Utility: return stock dict for looping in template
    def size_stock(self):
        return {
            "XXS": self.qty_xxs,
            "XS": self.qty_xs,
            "S": self.qty_s,
            "M": self.qty_m,
            "L": self.qty_l,
            "XL": self.qty_xl,
            "XXL": self.qty_xxl,
            "XXXL": self.qty_xxxl,
        }


@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)