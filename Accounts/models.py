import math
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.timezone import now

# ✅ Import UPDATED product models
from Products.models import (
    Product,
    ProductColor,
    ProductColorSize,
    Design,
    ProductImage
)

# ----------------- PROFILE MODEL ----------------- #
def profile_picture_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{instance.user.username}-{now().strftime('%d_%m_%Y_%H%M%S')}.{ext}"
    return "/static/images/logo.jpg"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# ----------------- ADDRESS MODEL ----------------- #
class Address(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="addresses")
    receiver_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50, default="India")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.receiver_name} - {self.city}"

    @property
    def full_address(self):
        return f"{self.address_line1}, {self.address_line2}, {self.city}, {self.state} - {self.postal_code}"

    class Meta:
        verbose_name_plural = "Addresses"


# ----------------- CART ITEM MODEL ----------------- #
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")

    # ✅ NEW: cart is based on Design (because shop is design-based)
    design = models.ForeignKey(Design, on_delete=models.CASCADE,null=True, blank=True, related_name="cart_items")

    # ✅ size is chosen by user (stock is on ProductColorSize)
    size = models.CharField(max_length=5, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("user", "design", "size")

    @property
    def product(self):
        return self.design.product

    @property
    def color(self):
        return self.design.color

    @property
    def product_type(self):
        return self.design.product_type

    @property
    def price(self):
        """Price from product_type (discounted if available)"""
        if self.product_type:
            return math.floor(self.product_type.discounted_price)
        return 0

    def subtotal(self):
        return self.price * self.quantity

    def get_image(self):
        """Return primary image for this design"""
        img = self.design.images.filter(is_primary=True).first() or self.design.images.first()
        if img:
            return img.image.url
        return "https://via.placeholder.com/100x100?text=No+Image"

    def __str__(self):
        return f"{self.user.username} - {self.design.name} ({self.size})"


# ----------------- WISHLIST MODEL ----------------- #
class Wishlist(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="wishlist_items")

    # ✅ NEW: Wishlist stores Design (not Product)
    design = models.ForeignKey(
        Design,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="wishlist_entries"
    )

    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "design")

    def __str__(self):
        return f"{self.user.username} - {self.design.name}"


# ----------------- ORDER MODEL ----------------- #
class Order(models.Model):
    ORDER_STATUS = [
        ("P", "Pending"),
        ("PR", "Processing"),
        ("S", "Shipped"),
        ("D", "Delivered"),
        ("C", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("COD", "Cash on Delivery"),
        ("ONLINE", "Online Payment"),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="COD")

    status = models.CharField(max_length=2, choices=ORDER_STATUS, default="P")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} - {self.profile.user.username}"


# ----------------- ORDER ITEM MODEL ----------------- #
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    # ✅ NEW: OrderItem stores Design
    design = models.ForeignKey(Design, on_delete=models.SET_NULL, null=True, blank=True)

    size = models.CharField(max_length=5, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    # ✅ store price at order time (so price doesn't change later)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def __str__(self):
        if self.design:
            return f"{self.design.name} ({self.size}) x {self.quantity}"
        return f"OrderItem #{self.id}"

    @property
    def total_price(self):
        return self.price * self.quantity

    @property
    def image_url(self):
        """Return primary image of design"""
        if self.design:
            img = self.design.images.filter(is_primary=True).first() or self.design.images.first()
            if img:
                return img.image.url
        return "https://via.placeholder.com/50"
