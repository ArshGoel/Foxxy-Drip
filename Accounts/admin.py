from django.contrib import admin
from .models import Profile, Address, CartItem

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'gender', 'date_joined')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('receiver_name', 'city', 'state', 'postal_code', 'is_default')
    list_filter = ('is_default', 'city', 'state')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'subtotal')
    search_fields = ('user__username', 'product__name')
