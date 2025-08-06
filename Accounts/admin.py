from django.contrib import admin
from .models import UserProfile, Address, CartItem

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile_number', 'gender', 'date_of_birth', 'newsletter_subscribed', 'created_at')
    search_fields = ('user__username', 'mobile_number')
    list_filter = ('gender', 'newsletter_subscribed', 'created_at')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'address_line1', 'city', 'state', 'pincode', 'is_default', 'created_at')
    search_fields = ('user_profile__user__username', 'city', 'state', 'pincode')
    list_filter = ('is_default', 'city', 'state')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'subtotal')
    search_fields = ('user__username', 'product__name')
