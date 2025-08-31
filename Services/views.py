import json
from django.contrib import messages
from django.shortcuts import render
from Accounts.models import Profile,Address,CartItem, Order, OrderItem
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductImage
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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, ProductColor, ProductColorSize, ProductDesign, ProductImage

@login_required
def upload_product(request):
    if request.method == "POST":
        # 1️⃣ Create product
        product = Product.objects.create(
            name=request.POST.get("name"),
            price=request.POST.get("price", 0.0)
        )

        # 2️⃣ Create colors + sizes
        color_names = request.POST.getlist("color_name[]")
        color_objs = []
        for idx, color_name in enumerate(color_names):
            if color_name.strip():
                color_obj = ProductColor.objects.create(product=product, name=color_name.strip())
                color_objs.append(color_obj)
                # Sizes
                for size in ["S","M","L","XL"]:
                    qty = request.POST.get(f"qty_{idx}_{size}", 0)
                    ProductColorSize.objects.create(color=color_obj, size=size, quantity=int(qty))

        # 3️⃣ Create designs and upload images
        design_names = request.POST.getlist("design_name[]")
        design_descs = request.POST.getlist("design_desc[]")
        design_color_indices = request.POST.getlist("design_color_index[]")  # index of color in color_objs

        for idx, name in enumerate(design_names):
            if name.strip():
                color_idx = int(design_color_indices[idx])
                color_obj = color_objs[color_idx]
                design_obj = ProductDesign.objects.create(
                    color=color_obj,
                    name=name.strip(),
                    description=design_descs[idx].strip()
                )
                # Upload images for this design
                images = request.FILES.getlist(f"design_images_{idx}")
                for img in images:
                    ProductImage.objects.create(
                        product=product,
                        color=color_obj,
                        design=design_obj,
                        image=img
                    )

        messages.success(request, "Product uploaded successfully!")
        return redirect("view_products")

    return render(request, "upload_product.html")


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    colors = product.colors.all() # type: ignore
    designs = ProductDesign.objects.filter(color__product=product)

    # Prepare sizes dict for each color so template always has S, M, L, XL
    for color in colors:
        sizes_dict = {size: 0 for size in ["S", "M", "L", "XL"]}
        for size_obj in color.sizes.all():
            sizes_dict[size_obj.size] = size_obj.quantity
        color.sizes_dict = sizes_dict  # attach to color object for template

    if request.method == "POST":
        # Update product
        product.name = request.POST.get("name")
        product.price = request.POST.get("price", 0.0) # type: ignore
        product.save()

        # ----------------- Handle Colors -----------------
        color_ids = request.POST.getlist("color_id[]")
        color_names = request.POST.getlist("color_name[]")

        for idx, name in enumerate(color_names):
            c_id = color_ids[idx] if idx < len(color_ids) else ''
            if c_id:  # existing color
                color = ProductColor.objects.get(id=c_id)
                color.name = name
                color.save()
            else:  # new color
                color = ProductColor.objects.create(product=product, name=name)
                if idx < len(color_ids):
                    color_ids[idx] = str(color.id) # type: ignore
                else:
                    color_ids.append(str(color.id)) # type: ignore

            # Update sizes
            for size in ["S", "M", "L", "XL"]:
                qty = request.POST.get(f"qty_{c_id or color.id}_{size}", 0) # type: ignore
                qty = int(qty)
                obj, _ = ProductColorSize.objects.get_or_create(color=color, size=size)
                obj.quantity = qty
                obj.save()

        # ----------------- Handle Designs -----------------
        design_ids = request.POST.getlist("design_id[]")
        design_names = request.POST.getlist("design_name[]")
        design_descs = request.POST.getlist("design_desc[]")
        design_color_index = request.POST.getlist("design_color_index[]")

        for idx, name in enumerate(design_names):
            if idx < len(design_color_index) and design_color_index[idx].isdigit():
                color_idx = int(design_color_index[idx])
                if color_idx < len(color_ids):
                    color = ProductColor.objects.get(id=color_ids[color_idx])
                else:
                    continue
            else:
                continue

            d_id = design_ids[idx] if idx < len(design_ids) else ''
            if d_id:
                design = ProductDesign.objects.get(id=d_id)
                design.name = name
                design.description = design_descs[idx]
                design.color = color
                design.save()
            else:
                design = ProductDesign.objects.create(
                    name=name,
                    description=design_descs[idx] if idx < len(design_descs) else "",
                    color=color
                )

            images = request.FILES.getlist(f"design_images_{d_id or 'new'+str(idx)}")
            for img in images:
                ProductImage.objects.create(product=product, color=color, design=design, image=img)

        # ----------------- Handle deleted images -----------------
        delete_ids = request.POST.getlist("delete_images[]")
        for img_id in delete_ids:
            ProductImage.objects.filter(id=img_id).delete()

        messages.success(request, "Product updated successfully!")
        return redirect("view_products")

    return render(request, "edit_product.html", {
        "product": product,
        "colors": colors,
        "designs": designs
    })


# ---------- Product List ----------
def product_list(request):
    products = Product.objects.all().order_by('-date_added')

    return render(request, "product_list.html", {"products": products})

def product_designs_view(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    designs = []
    for color in product.colors.all(): # type: ignore
        for design in color.designs.all():
            images = design.images.all()
            designs.append({"color": color.name, "design": design, "images": images})
    return render(request, "product_designs.html", {"product": product, "designs": designs})

# ---------- View Single Product ----------
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

# @login_required
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
def add_to_cart(request, design_id):
    # Get the selected design
    design = get_object_or_404(ProductDesign, id=design_id)

    # Design already links to product, color, and type
    product = design.color.product
    color = design.color
    size = request.POST.get("size")   # must be chosen
    quantity = int(request.POST.get("quantity", 1))

    # Create / update CartItem
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        color=color,
        design=design,
        size=size or "",
        defaults={"quantity": quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect("view_cart")


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

# def add_to_cart(request, product_id):
#     cart_items = request.session.get("cart_items", [])
#     cart_items.append(product_id)
#     request.session["cart_items"] = cart_items
#     messages.success(request, "Product added to cart!")
#     return redirect("view_cart")


from django.db import transaction

@login_required
def checkout(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.warning(request, "Please complete your profile before checkout.")
        return redirect("complete_profile")

    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    if not cart_items:
        messages.warning(request, "Your cart is empty. Add some products before checkout.")
        return redirect("view_cart")

    addresses = profile.addresses.all()  # type: ignore

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

                # ✅ Create OrderItems & decrease stock
                for item in cart_items:
                    product = item.product
                    design = getattr(item, "design", None)  # get design if exists
                    size = item.size
                    qty_needed = item.quantity

                    # Find size entry in ProductColorSize
                    size_entry = ProductColorSize.objects.filter(
                        color__product=product,
                        size=size
                    ).first()

                    if not size_entry:
                        messages.error(request, f"Invalid size {size} for {product.name}")
                        raise transaction.TransactionManagementError("Invalid size")

                    if size_entry.quantity < qty_needed:
                        messages.error(
                            request,
                            f"Not enough stock for {product.name} ({size}). Available: {size_entry.quantity}"
                        )
                        raise transaction.TransactionManagementError("Insufficient stock")

                    # Deduct stock
                    size_entry.quantity -= qty_needed
                    size_entry.save()

                    # Create OrderItem with design
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        design=design,
                        size=size,
                        quantity=qty_needed,
                        price=item.price
                    )

                # Clear cart
                cart_items.delete()

        except transaction.TransactionManagementError:
            return redirect("view_cart")

        send_order_emails(order, request=request)
        messages.success(request, f"Order #{order.id} placed successfully!")  # type: ignore
        return redirect("order_detail", order_id=order.id)  # type: ignore

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

import os, zipfile, tempfile, csv
from django.http import FileResponse
from django.apps import apps
from django.conf import settings
from datetime import datetime

@staff_member_required
def download_backup(request):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    zip_filename = tmp.name

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        # ✅ Dump each model into CSV
        for model in apps.get_models():
            model_name = model.__name__.lower()
            csv_file = os.path.join(settings.BASE_DIR, f"{model_name}_{timestamp}.csv")

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                fields = [field.name for field in model._meta.fields]
                writer.writerow(fields)  # header row
                for obj in model.objects.all():
                    row = [getattr(obj, field) for field in fields]
                    writer.writerow(row)

            # Add to zip
            zipf.write(csv_file, f"db/{model_name}.csv")
            os.remove(csv_file)

        # ✅ Add media folder
        if os.path.exists(settings.MEDIA_ROOT):
            for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, settings.MEDIA_ROOT)
                    zipf.write(filepath, os.path.join("media", arcname))

    return FileResponse(open(zip_filename, "rb"), as_attachment=True, filename=f"backup_{timestamp}.zip")

def design_detail(request, design_id):
    design = get_object_or_404(ProductDesign, id=design_id)
    return render(request, "design_detail.html", {"design": design})
