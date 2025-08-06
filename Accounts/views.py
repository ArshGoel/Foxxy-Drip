from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from Services.models import Product
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from Services.models import Product
from .models import CartItem


def home(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    return render(request, 'home.html', {'cart_count': cart_count})

def FAQ(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    return render(request, 'FAQ.html', {'cart_count': cart_count})

def aboutus(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    return render(request, 'aboutus.html', {'cart_count': cart_count})

def shop(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    products = Product.objects.all()

    cart_product_ids = set()
    cart_quantities = {}

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            cart_product_ids.add(item.product.product_id)
            cart_quantities[item.product.product_id] = item.quantity

    context = {
        'products': products,
        'cart_product_ids': cart_product_ids,
        'cart_quantities': cart_quantities
    }
    return render(request, 'shop.html', context)

@login_required
def update_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if request.POST.get("action") == "increase":
        cart_item.quantity += 1
    elif request.POST.get("action") == "decrease":
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            return redirect('shop')
    cart_item.save()
    return redirect('shop')

def customize(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    return render(request, 'customize.html', {'cart_count': cart_count})

def contactus(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            send_mail(
                subject=f"Contact Us:- New Message from {name}",
                message=message,
                from_email=email,
                recipient_list=['foxxydrip.contact@gmail.com'], 
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contactus')  # Make sure this matches your URL name
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'contactus.html', {'cart_count': cart_count})

def login_user(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')  # adapt this to your input name
        password = request.POST.get('password')
        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # or wherever you want
        else:
            messages.error(request, "Invalid credentials")
            return redirect('/')  # or reload modal
    return redirect('/')

def register_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('/')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
            return redirect('/')

        user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
        login(request, user)
        return redirect('/')

    return redirect('/')



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect("view_cart")

@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in items)
    return render(request, "view_cart.html", {"items": items, "total": total})

@login_required
def remove_from_cart(request, product_id):
    item = get_object_or_404(CartItem, user=request.user, product__product_id=product_id)
    item.delete()
    return redirect("view_cart")