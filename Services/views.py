from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from Accounts.models import Profile,Address,CartItem, Order, OrderItem
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

def send_order_emails(order, request=None):
    """
    Sends:
      1) Order confirmation to the customer
      2) New order notification to the admin(s)
    """
    # Useful URLs (optional)
    order_detail_url = None
    admin_order_url = None

    if request:
        try:
            order_detail_url = request.build_absolute_uri(
                reverse("order_detail", kwargs={"order_id": order.id})
            )
        except Exception:
            pass
        try:
            admin_order_url = request.build_absolute_uri(
                reverse("admin_order_detail", kwargs={"order_id": order.id})
            )
        except Exception:
            pass

    # ---------- Customer email ----------
    user_email = order.profile.user.email
    if user_email:
        ctx_user = {
            "order": order,
            "order_detail_url": order_detail_url,
        }
        subject_user = f"Foxxy Drip — Order Confirmation #{order.id}"
        html_body_user = render_to_string("emails/order_confirmation_user.html", ctx_user)
        text_body_user = f"Your order #{order.id} has been received. Total: ₹{order.total_price}."

        msg_user = EmailMultiAlternatives(
            subject_user,
            text_body_user,
            settings.EMAIL_HOST_USER,
            [user_email],
        )
        msg_user.attach_alternative(html_body_user, "text/html")
        msg_user.send(fail_silently=False)

    # ---------- Admin email ----------
    admin_recipients = getattr(settings, "ORDER_ADMIN_EMAILS", []) or [settings.EMAIL_HOST_USER]
    if admin_recipients:
        ctx_admin = {
            "order": order,
            "admin_order_url": admin_order_url,
        }
        subject_admin = f"New Order Received — #{order.id}"
        html_body_admin = render_to_string("emails/order_notification_admin.html", ctx_admin)
        text_body_admin = f"New order #{order.id} placed by {order.profile.user.username}. Total: ₹{order.total_price}"

        msg_admin = EmailMultiAlternatives(
            subject_admin,
            text_body_admin,
            settings.EMAIL_HOST_USER,
            ["foxxydrip13@gmail.com"],
        )
        msg_admin.attach_alternative(html_body_admin, "text/html")
        msg_admin.send(fail_silently=False)


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

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .models import Product

@login_required
def upload_product(request):
    if request.method == 'POST':
        product = Product.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            category=request.POST['category'],
            price=request.POST['price'],
            color=request.POST['color'],
            image=request.FILES['image'],
            qty_xxs=request.POST.get('qty_xxs', 0),
            qty_xs=request.POST.get('qty_xs', 0),
            qty_s=request.POST.get('qty_s', 0),
            qty_m=request.POST.get('qty_m', 0),
            qty_l=request.POST.get('qty_l', 0),
            qty_xl=request.POST.get('qty_xl', 0),
            qty_xxl=request.POST.get('qty_xxl', 0),
            qty_xxxl=request.POST.get('qty_xxxl', 0),
        )
        messages.success(request, "Product uploaded successfully!")
        return redirect('view_products')

    return render(request, 'upload_product.html', {"Product": Product})


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

        # Update quantities
        product.qty_xxs = int(request.POST.get('qty_xxs', 0))
        product.qty_xs = int(request.POST.get('qty_xs', 0))
        product.qty_s = int(request.POST.get('qty_s', 0))
        product.qty_m = int(request.POST.get('qty_m', 0))
        product.qty_l = int(request.POST.get('qty_l', 0))
        product.qty_xl = int(request.POST.get('qty_xl', 0))
        product.qty_xxl = int(request.POST.get('qty_xxl', 0))
        product.qty_xxxl = int(request.POST.get('qty_xxxl', 0))

        product.save()

        messages.success(request, "✅ Product updated successfully!")
        return redirect('product_list')

    return render(request, 'edit_product.html', {"product": product})


# ---------- Product List ----------
def product_list(request):
    products = Product.objects.all().order_by('-date_added')
    return render(request, 'product_list.html', {"products": products})

# ---------- View Single Product ----------
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

@login_required
def view_product(request, pk):
    product = get_object_or_404(Product, product_id=pk)

    if request.method == "POST":
        size = request.POST.get("size")
        qty = int(request.POST.get("quantity", 1))

        if not size:
            messages.error(request, "Please select a size before adding to cart.")
        else:
            # Check if same product + same size already in cart
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                size=size,   # ✅ include size
                defaults={"quantity": qty}
            )
            if not created:
                cart_item.quantity += qty
                cart_item.save()

            messages.success(request, f"{product.name} (Size {size}) x{qty} added to your cart!")
            return redirect("view_cart")

    return render(request, "view_product.html", {"product": product})

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, "view_cart.html", {"cart_items": cart_items, "total": total})


@login_required 
def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if request.method == "POST":
        try:
            qty = int(request.POST.get("quantity", 1))
            if qty > 0:
                cart_item.quantity = qty
                cart_item.save()
                messages.success(request, "Cart updated successfully.")
            else:
                cart_item.delete()
                messages.info(request, "Item removed from cart (quantity set to 0).")
        except ValueError:
            messages.error(request, "Invalid quantity.")
    return redirect("view_cart")


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("view_cart")

def view_products(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})

def add_to_cart(request, product_id):
    cart_items = request.session.get("cart_items", [])
    cart_items.append(product_id)
    request.session["cart_items"] = cart_items
    messages.success(request, "Product added to cart!")
    return redirect("view_cart")


from django.db import transaction

@login_required
def checkout(request):
    profile = get_object_or_404(Profile, user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    if not cart_items:
        messages.warning(request, "Your cart is empty. Add some products before checkout.")
        return redirect("view_cart")

    addresses = profile.addresses.all() #type:ignore

    if request.method == "POST":
        address_id = request.POST.get("address")

        if not addresses.exists():
            messages.error(request, "You need to add an address before placing an order.")
            return redirect("checkout")

        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect("checkout")

        address = Address.objects.filter(id=address_id, profile=profile).first()
        if not address:
            messages.error(request, "Invalid address selected.")
            return redirect("checkout")

        try:
            with transaction.atomic():
                # ✅ Create Order
                order = Order.objects.create(
                    profile=profile,
                    address=address,
                    total_price=total,
                    status="P"
                )

                # Create OrderItems & decrease stock per size
                for item in cart_items:
                    product = item.product
                    size = item.size
                    qty_needed = item.quantity

                    # ✅ Map size → field name
                    size_field_map = {
                        "XXS": "qty_xxs",
                        "XS": "qty_xs",
                        "S": "qty_s",
                        "M": "qty_m",
                        "L": "qty_l",
                        "XL": "qty_xl",
                        "XXL": "qty_xxl",
                        "XXXL": "qty_xxxl",
                    }

                    if size not in size_field_map:
                        messages.error(request, f"Invalid size {size} for {product.name}")
                        raise transaction.TransactionManagementError("Invalid size")

                    stock_field = size_field_map[size]
                    current_stock = getattr(product, stock_field)

                    # ✅ Check stock availability
                    if current_stock < qty_needed:
                        messages.error(request, f"Not enough stock for {product.name} ({size}). Available: {current_stock}")
                        raise transaction.TransactionManagementError("Insufficient stock")

                    # ✅ Deduct stock
                    setattr(product, stock_field, current_stock - qty_needed)
                    product.save()

                    # Create OrderItem
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        size=size,
                        quantity=qty_needed,
                        price=product.price
                    )

                # Clear cart after success
                cart_items.delete()

        except transaction.TransactionManagementError:
            return redirect("view_cart")

        send_order_emails(order, request=request)
        messages.success(request, f"Order #{order.id} placed successfully!")  # type:ignore
        return redirect("order_detail", order_id=order.id)  # type:ignore

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "addresses": addresses
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, profile__user=request.user)
    return render(request, "order_detail.html", {"order": order})


@login_required
def orders(request):
    profile = Profile.objects.get(user=request.user)
    orders = Order.objects.filter(profile=profile).order_by("-created_at")
    return render(request, "orders.html", {"orders": orders})

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

# List all orders
@staff_member_required   # ✅ restrict to staff/admin
def admin_orders_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin_orders_list.html", {"orders": orders})

# View single order
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin_order_detail.html", {"order": order})

# Update order status
@staff_member_required
def admin_update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Order.ORDER_STATUS).keys():
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.") # type:ignore
        else:
            messages.error(request, "Invalid status.")
        return redirect("admin_order_detail", order_id=order.id) # type:ignore 


import os, zipfile, tempfile
from django.http import FileResponse
from django.core import management
from django.conf import settings
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def download_backup(request):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    zip_filename = tmp.name

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        # Dump DB
        dump_file = os.path.join(settings.BASE_DIR, f"db_dump_{timestamp}.json")
        with open(dump_file, "w", encoding="utf-8") as f:
            management.call_command("dumpdata", "--natural-primary", "--natural-foreign", indent=2, stdout=f)

        zipf.write(dump_file, f"db_dump_{timestamp}.json")
        os.remove(dump_file)

        # Add media
        if os.path.exists(settings.MEDIA_ROOT):
            for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, settings.MEDIA_ROOT)
                    zipf.write(filepath, os.path.join("media", arcname))

    return FileResponse(open(zip_filename, "rb"), as_attachment=True, filename=f"backup_{timestamp}.zip")