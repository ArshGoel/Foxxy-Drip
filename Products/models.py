from decimal import Decimal
from django.db import models, transaction
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField  # type: ignore

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
class Product(models.Model):
    product_id = models.CharField(max_length=20, primary_key=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"
class ProductType(models.Model):
    TYPE_CHOICES = [
        ("plain", "Plain"),
        ("printed", "Printed"),
        ("embroidery", "Embroidery"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="types"
    )
    type_name = models.CharField(max_length=20, choices=TYPE_CHOICES)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    class Meta:
        unique_together = ("product", "type_name")

    def clean(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError("Discount price must be less than price")

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    def __str__(self):
        return f"{self.product.name} - {self.type_name}"
class ProductColor(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="colors"
    )
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("product", "name")

    def __str__(self):
        return f"{self.product.name} - {self.name}"
class ProductColorSize(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
    ]

    color = models.ForeignKey(
        ProductColor, on_delete=models.CASCADE, related_name="sizes"
    )
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("color", "size")
        indexes = [
            models.Index(fields=["color", "size"]),
        ]

    def __str__(self):
        return f"{self.color.name} - {self.size} ({self.quantity})"
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="images"
    )

    color = models.ForeignKey(
        ProductColor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="images"
    )

    image = CloudinaryField(
        "image",
        transformation=[
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    is_primary = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)
    def clean(self):
        if not self.product:
            raise ValidationError("Image must belong to a product")

    def __str__(self):
        parts = [self.product.name]
        if self.product_type:
            parts.append(self.product_type.type_name)
        if self.color:
            parts.append(self.color.name)
        return " - ".join(parts)
@transaction.atomic
def reduce_stock(color, size, qty):
    if qty <= 0:
        raise ValidationError("Quantity must be greater than zero")

    stock = (
        ProductColorSize.objects
        .select_for_update()
        .get(color=color, size=size)
    )

    if stock.quantity < qty:
        raise ValidationError("Out of stock")

    stock.quantity -= qty
    stock.save()
