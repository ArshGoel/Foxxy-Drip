from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Accounts.models import Profile,Address


def wishlist(request):
    return render(request, 'wishlist.html') 

def upload_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        price = request.POST.get('price')
        color = request.POST.get('color')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')

        # Get multiple checkbox values
        sizes = request.POST.getlist('available_sizes')
        try:
            available_sizes = json.dumps(sizes)
        except Exception:
            return render(request, 'upload_product_manual.html', {
                'error': 'Sizes must be valid.',
            })

        product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            available_sizes=available_sizes,
            color=color,
            stock=stock,
            image=image
        )
        product.save()
        return redirect('product_list')

    return render(request, 'upload_product.html')

def product_list(request):
    products = Product.objects.all().order_by('-date_added')
    
    # Attach parsed sizes to each product
    for p in products:
        try:
            p.size_list = json.loads(p.available_sizes)
        except json.JSONDecodeError:
            p.size_list = []

    return render(request, 'product_list.html', {'products': products})

def edit_product(request, product_id):
    product = Product.objects.get(product_id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.color = request.POST.get('color')
        product.stock = request.POST.get('stock')

        sizes = request.POST.getlist('available_sizes')
        product.available_sizes = json.dumps(sizes)

        # Handle image update only if a new one is uploaded
        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        return redirect('product_list')

    try:
        size_list = json.loads(product.available_sizes)
    except:
        size_list = []

    return render(request, 'edit_product.html', {
        'product': product,
        'size_list': size_list,
    })


def view_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    try:
        sizes = json.loads(product.available_sizes)
    except:
        sizes = []

    context = {
        'product': product,
        'sizes': sizes
    }
    return render(request, 'view_product.html', context)



# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def manage_address(request):
    profile = get_object_or_404(Profile, user=request.user)

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

        if is_default:
            Address.objects.filter(profile=profile, is_default=True).update(is_default=False)

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
    addresses = profile.addresses.all() # type: ignore
    return render(request, "manage_address.html", {"addresses": addresses})


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

    return render(request, "edit_address.html", {"address": address})




