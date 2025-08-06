from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
from django.db import models
from django.utils.deconstruct import deconstructible

@deconstructible
class ProductImagePath:
    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{instance.product_id}.{ext}"
        return os.path.join('products', filename)
    

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Tshirt', 'T-shirt'),
        ('Acid Wash T-Shirt', 'Acid Wash T-Shirt'),
        ('Hoodie', 'Hoodie'),
    ]

    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Extra Extra Large'),
    ]

    product_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available_sizes = models.CharField(max_length=100, default='')
    color = models.CharField(max_length=30)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to=ProductImagePath())
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def size_list(self):
        return [s.strip() for s in self.available_sizes.split(',') if s.strip()]

    @size_list.setter
    def size_list(self, sizes):
        if isinstance(sizes, list):
            self.available_sizes = ",".join(sizes)
        else:
            raise ValueError("size_list must be a list")
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.product_id:
            last = Product.objects.order_by('-product_id').first()
            next_id = 1
            if last and last.product_id[1:].isdigit():
                next_id = int(last.product_id[1:]) + 1
            self.product_id = f"P{next_id:03}"

        # delete old image if replacing
        try:
            this = Product.objects.get(product_id=self.product_id)
            if this.image != self.image:
                this.image.delete(save=False)
        except Product.DoesNotExist:
            pass

        super().save(*args, **kwargs)

@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)