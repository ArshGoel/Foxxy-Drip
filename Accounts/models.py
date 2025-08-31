import os
from django.db import models
from django.utils import timezone
from Services.models import Product
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.db.models.signals import post_delete

# ----------------- PROFILE MODEL ----------------- #
def profile_picture_upload_path(instance, filename):
    # Get file extension (e.g. .jpg, .png)
    ext = filename.split('.')[-1]
    
    # Ensure uniqueness: username + timestamp
    filename = f"{instance.user.username}-{now().strftime('%d_%m_%Y_%H%M%S')}.{ext}"
    
    # Save inside "profile_images/"
    return os.path.join('profile_images', filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path,blank=True,null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_delete, sender=Profile)
def delete_profile_picture(sender, instance, **kwargs):
    if instance.profile_picture:
        instance.profile_picture.delete(save=False)

@receiver(pre_save, sender=Profile)
def auto_delete_old_profile_picture_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return  
    try:
        old_pic = Profile.objects.get(pk=instance.pk).profile_picture
    except Profile.DoesNotExist:
        return
    new_pic = instance.profile_picture
    if old_pic and (not new_pic or old_pic != new_pic):
        old_pic.delete(save=False)


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

    class Meta:
        verbose_name_plural = "Addresses"

from Services.models import ProductColor,ProductDesign
# ----------------- CART ITEM MODEL ----------------- #
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, null=True, blank=True)
    design = models.ForeignKey(ProductDesign, on_delete=models.CASCADE, null=True, blank=True)
    size = models.CharField(max_length=5, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def price(self):
        """Return price from design (discounted if available)"""
        if self.design:  
            if self.design.discounted_price:
                return self.design.discounted_price
            return self.design.price
        return 0  # fallback if no design

    def subtotal(self):
        return self.price * self.quantity

    def get_image(self):
        """Return proper image for cart item"""
        if self.design and self.design.images.exists():#type:ignore
            return self.design.images.first().image.url#type:ignore
        elif self.color and self.color.images.exists():#type:ignore
            return self.color.images.first().image.url#type:ignore
        elif self.product.images.exists():#type:ignore
            return self.product.images.first().image.url#type:ignore
        return "https://via.placeholder.com/100x100?text=No+Image"

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.design.name if self.design else 'No design'})"


# ----------------- WISHLIST MODEL ----------------- #
class Wishlist(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'product')

    def __str__(self):
        return f"{self.profile.user.username} - {self.product.name}"


# ----------------- ORDER MODEL ----------------- #
class Order(models.Model):
    ORDER_STATUS = [
        ('P', 'Pending'),
        ('PR', 'Processing'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('C', 'Cancelled'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=2, choices=ORDER_STATUS, default='P')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.id} - {self.profile.user.username}" # type: ignore


# ----------------- ORDER ITEM MODEL ----------------- #
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=5, blank=True, null=True)   # ✅ added
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at purchase time

    def __str__(self):
        return f"{self.product.name} ({self.size}) x {self.quantity}"  # type: ignore

    @property
    def total_price(self):
        return self.price * self.quantity
    
