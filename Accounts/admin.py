# accounts/admin.py
from django.contrib import admin
from .models import Profile, Address, CartItem, Wishlist, Order, OrderItem

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "phone_number", "date_joined")
    search_fields = ("user__username", "phone_number")
    list_filter = ("gender",)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("receiver_name", "city", "state", "is_default", "profile")
    list_filter = ("is_default", "state", "city")
    search_fields = ("receiver_name", "city", "postal_code", "phone")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "subtotal")
    search_fields = ("user__username", "product__name")

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("profile", "product", "date_added")
    search_fields = ("profile__user__username", "product__name")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "profile__user__username")
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "total_price")
    search_fields = ("order__id", "product__name")
