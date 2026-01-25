from django.apps import apps
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from django.db import transaction
import os, zipfile, tempfile, csv
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from user_sessions.models import Session
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from Accounts.models import Profile,Address,CartItem, Order, OrderItem
from django.contrib.admin.views.decorators import staff_member_required
# from .models import Product, ProductColor, ProductColorSize, ProductDesign, ProductImage


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)
    return render(request, "view_cart.html", {"cart_items": cart_items, "total": total})

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
        messages.warning(request, "Your cart is empty. Add some products first.")
        return redirect("view_cart")

    addresses = profile.addresses.all() #type:ignore

    if request.method == "POST":
        address_id = request.POST.get("address")
        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect("checkout")

        request.session["checkout_address"] = address_id  # ✅ save temporarily
        return redirect("payment_page")

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "addresses": addresses
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal

from Products.models import ProductColorSize
# from .utils import send_order_emails   # keep your function import



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
        messages.warning(request, "Please complete your profile before checkout.")
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
    
    if request.method == "POST":
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    
    return redirect("view_cart")



@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, profile__user=request.user)
    return render(request, "order_detail.html", {"order": order})


@login_required
def orders(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.warning(request, "Please complete your profile before checkout.")
        return redirect("complete_profile")
    orders = Order.objects.filter(profile=profile).order_by("-created_at")
    return render(request, "orders.html", {"orders": orders})


@staff_member_required  
def admin_orders_list(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin_orders_list.html", {"orders": orders})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "admin_order_detail.html", {"order": order})


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




@login_required
def active_sessions(request):
    # List all sessions for this user
    sessions = Session.objects.filter(user=request.user)
    return render(request, "active_sessions.html", {"sessions": sessions})


@login_required
def logout_other_session(request, session_key):
    # End a specific session (other than current one)
    Session.objects.filter(user=request.user, session_key=session_key).delete()
    return redirect("active_sessions")

@login_required
def payment_page(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        messages.warning(request, "Please complete your profile before checkout.")
        return redirect("complete_profile")

    cart_items = CartItem.objects.filter(user=request.user).select_related("design")

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("view_cart")

    total = sum(item.subtotal() for item in cart_items)
    if total <= 0:
        messages.error(request, "Invalid cart total.")
        return redirect("view_cart")

    address_id = request.session.get("checkout_address")
    address = Address.objects.filter(id=address_id, profile=profile).first()

    if request.method == "POST":
        payment_mode = request.POST.get("payment_mode")

        if not payment_mode:
            messages.error(request, "Please select a payment method.")
            return redirect("payment_page")

        # ✅ COD FLOW (UNCHANGED)
        if payment_mode == "COD":
            try:
                with transaction.atomic():

                    order = Order.objects.create(
                        profile=profile,
                        address=address,
                        total_price=Decimal(total),
                        status="P",
                        payment_mode="COD"
                    )

                    for item in cart_items:
                        design = item.design
                        size = item.size
                        qty_needed = item.quantity

                        if not design or not size:
                            raise ValueError("Invalid cart item.")

                        size_entry = ProductColorSize.objects.select_for_update().filter(
                            color=design.color,
                            size=size
                        ).first()

                        if not size_entry:
                            raise ValueError(
                                f"Size {size} not available for {design.name}"
                            )

                        if size_entry.quantity < qty_needed:
                            raise ValueError(
                                f"Only {size_entry.quantity} left for {design.name} ({size})"
                            )

                        OrderItem.objects.create(
                            order=order,
                            design=design,
                            size=size,
                            quantity=qty_needed,
                            price=Decimal(item.price)
                        )

                    # reduce stock
                    for item in cart_items:
                        size_entry = ProductColorSize.objects.select_for_update().filter(
                            color=item.design.color,
                            size=item.size
                        ).first()

                        size_entry.quantity -= item.quantity
                        size_entry.save()

                    cart_items.delete()
                    messages.success(
                        request, f"Order #{order.id} placed successfully!"
                    )
                    return redirect("order_detail", order_id=order.id)

            except Exception as e:
                messages.error(request, f"Error placing order: {e}")
                return redirect("payment_page")

        # ✅ ONLINE FLOW (NEW, CLEAN)
        if payment_mode == "PHONEPE":
            return redirect("start_phonepe_payment")

    return render(request, "payment_page.html", {
        "cart_items": cart_items,
        "total": total,
        "address": address
    })
