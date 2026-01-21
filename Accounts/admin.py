from django.contrib import admin
from .models import Profile, Address, CartItem, Wishlist, Order, OrderItem


# ------------------ Inline Admins ------------------

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# ------------------ Profile Admin ------------------

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone_number", "gender", "date_joined")
    search_fields = ("user__username", "user__email", "phone_number")
    list_filter = ("gender", "date_joined")
    inlines = [AddressInline]


# ------------------ Address Admin ------------------

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "receiver_name", "city", "state", "postal_code", "is_default")
    search_fields = ("profile__user__username", "receiver_name", "city", "state", "postal_code")
    list_filter = ("state", "city", "is_default")


# ------------------ Cart Item Admin ------------------

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "design", "size", "quantity")
    search_fields = ("user__username", "design__name", "design__product__name")
    list_filter = ("size",)


# ------------------ Wishlist Admin ------------------

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "design", "date_added")
    search_fields = ("user__user__username", "design__name", "design__product__name")
    list_filter = ("date_added",)


# ------------------ Order Admin ------------------

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "status", "payment_mode", "total_price", "created_at")
    search_fields = ("profile__user__username", "id")
    list_filter = ("status", "payment_mode", "created_at")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]


# ------------------ OrderItem Admin ------------------

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "design", "size", "quantity", "price")
    search_fields = ("order__id", "design__name", "design__product__name")
    list_filter = ("size",)
