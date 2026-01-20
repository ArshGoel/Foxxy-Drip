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
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError

class ProductType(models.Model):
    TYPE_CHOICES = [
        ("plain", "Plain"),
        ("printed", "Printed"),
        ("embroidery", "Embroidery"),
    ]

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="types"
    )
    type_name = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Marked Price (MRP)
    price = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )

    # Selling Price
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00"),
        blank=True, null=True
    )

    def clean(self):
        # price should never be negative
        if self.price < 0:
            raise ValidationError("Price cannot be negative")

        # if discount_price exists, it must be valid
        if self.discount_price is not None:
            if self.discount_price < 0:
                raise ValidationError("Selling price cannot be negative")

            if self.discount_price >= self.price and self.price > 0:
                raise ValidationError("Selling price must be less than marked price")

    @property
    def discounted_price(self):
        """If discount_price is set & valid, return it else return original price"""
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def discount_amount(self):
        """How much customer saves"""
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price:
            return self.price - self.discount_price
        return Decimal("0.00")

    @property
    def discount_percent(self):
        """Calculate % off automatically"""
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price and self.price > 0:
            return round(100 - (self.discount_price / self.price * 100))
        return 0

    class Meta:
        unique_together = ("product", "type_name")

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
class Design(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="designs")
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name="designs")
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name="designs")

    position = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=150,default="Default Design Name")
    description = models.TextField(blank=True, null=True)
    show_in_shop = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["product", "product_type", "color"]),
        ]
        ordering = ["position", "-id"]
    def clean(self):
        if self.product_type.product != self.product:
            raise ValidationError("ProductType does not belong to this product")
        if self.color.product != self.product:
            raise ValidationError("Color does not belong to this product")

    def __str__(self):
        return f"{self.name} ({self.product.name} - {self.product_type.type_name} - {self.color.name})"


class ProductImage(models.Model):
    design = models.ForeignKey(
        Design, on_delete=models.CASCADE, related_name="images"
    )

    image = CloudinaryField(
        "image",
        transformation=[
            {"quality": "auto"},
            {"fetch_format": "auto"},
        ],
    )

    # ✅ primary now per design (not product/type/color)
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                design=self.design,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.design.name} - {'Primary' if self.is_primary else 'Image'}"
    
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
