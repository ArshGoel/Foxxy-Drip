from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Accounts.models import Profile,Address

@login_required
def manage_address(request):
    # Check if profile exists for the logged-in user
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect("complete_profile")  # redirect if profile not found

    # Handle POST (Add New Address)
    if request.method == "POST":
        receiver_name = request.POST.get("receiver_name")
        phone = request.POST.get("phone")
        address_line1 = request.POST.get("address_line1")
        address_line2 = request.POST.get("address_line2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")
        country = request.POST.get("country", "India")
        is_default = bool(request.POST.get("is_default"))

        # Ensure only one default address
        if is_default:
            Address.objects.filter(profile=profile, is_default=True).update(is_default=False)

        # Create new address
        Address.objects.create(
            profile=profile,
            receiver_name=receiver_name,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default
        )

        messages.success(request, "Address added successfully!")
        return redirect("manage_address")

    # GET - Show existing addresses
    addresses = profile.addresses.all()  # type: ignore
    return render(request, "address/manage_address.html", {"addresses": addresses})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, profile__user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully!")
    return redirect("manage_address")

@login_required
def make_default_address(request, address_id):
    profile = get_object_or_404(Profile, user=request.user)
    address = get_object_or_404(Address, id=address_id, profile=profile)

    # Set all to non-default first
    Address.objects.filter(profile=profile, is_default=True).update(is_default=False)

    # Set the chosen address as default
    address.is_default = True
    address.save()

    messages.success(request, "Default address updated successfully!")
    return redirect("manage_address")

@login_required
def edit_address(request, address_id):
    profile = get_object_or_404(Profile, user=request.user)
    address = get_object_or_404(Address, id=address_id, profile=profile)

    if request.method == "POST":
        address.receiver_name = request.POST.get("receiver_name")
        address.phone = request.POST.get("phone")
        address.address_line1 = request.POST.get("address_line1")
        address.address_line2 = request.POST.get("address_line2")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.postal_code = request.POST.get("postal_code")
        address.country = request.POST.get("country", "India")
        is_default = bool(request.POST.get("is_default"))

        if is_default:
            Address.objects.filter(profile=profile, is_default=True).update(is_default=False)

        address.is_default = is_default
        address.save()

        messages.success(request, "Address updated successfully!")
        return redirect("manage_address")

    return render(request, "address/edit_address.html", {"address": address})

def wishlist(request):
    return render(request, 'wishlist.html') 

@login_required
def upload_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        price = request.POST.get('price')
        color = request.POST.get('color')
        image = request.FILES.get('image')

        product = Product.objects.create(
            name=name,
            description=description,
            category=category,
            price=price,
            color=color,
            image=image
        )

        # Save sizes with quantity
        sizes = request.POST.getlist('sizes[]')
        quantities = request.POST.getlist('quantities[]')
        for size, qty in zip(sizes, quantities):
            if size and qty.isdigit():
                ProductSize.objects.create(product=product, size=size, quantity=int(qty))

        messages.success(request, "Product uploaded successfully!")
        return redirect('view_products')

    return render(request, 'upload_product.html')


# ---------- Product List ----------
def product_list(request):
    products = Product.objects.all().order_by('-date_added')
    return render(request, 'product_list.html', {"products": products})


# ---------- Edit Product ----------
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.color = request.POST.get('color')

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()

        # Update sizes
        product.sizes.all().delete()
        sizes = request.POST.getlist('sizes[]')
        quantities = request.POST.getlist('quantities[]')
        for size, qty in zip(sizes, quantities):
            if size and qty.isdigit():
                ProductSize.objects.create(product=product, size=size, quantity=int(qty))

        messages.success(request, "Product updated successfully!")
        return redirect('view_products')

    return render(request, 'edit_product.html', {"product": product, "sizes": product.sizes.all()})


# ---------- View Single Product ----------
def view_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    sizes = product.sizes.all()  # Related ProductSize
    return render(request, 'view_product.html', {"product": product, "sizes": sizes})

def view_cart(request):
    cart_items = request.session.get("cart_items", [])
    return render(request, "view_cart.html", {"cart_items": cart_items})

def view_products(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})

def add_to_cart(request, product_id):
    cart_items = request.session.get("cart_items", [])
    cart_items.append(product_id)
    request.session["cart_items"] = cart_items
    messages.success(request, "Product added to cart!")
    return redirect("view_cart")