from django.shortcuts import render

# Create your views here.
import uuid, requests, json
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PaymentTransaction
from Accounts.models import CartItem
from django.contrib import messages


from decimal import Decimal
from django.db import transaction
from Accounts.models import Order, OrderItem
from Accounts.models import CartItem, Address, Profile
from Products.models import ProductColorSize
def create_order_from_cart(user):
    """
    Creates Order + OrderItems from cart
    Reduces stock
    Clears cart

    Called ONLY after PhonePe payment SUCCESS
    """

    profile = Profile.objects.select_related().get(user=user)
    cart_items = CartItem.objects.select_related("design").filter(user=user)

    if not cart_items.exists():
        # Nothing to process (idempotency safety)
        return

    # Get selected checkout address
    address = Address.objects.filter(
        profile=profile,
        is_default=True
    ).first()

    if not address:
        raise Exception("No delivery address found")

    total = sum(item.subtotal() for item in cart_items)

    with transaction.atomic():

        # ✅ Create Order
        order = Order.objects.create(
            profile=profile,
            address=address,
            total_price=Decimal(total),
            status="P",               # or CONFIRMED if you prefer
            payment_mode="ONLINE"
        )

        # ✅ Create OrderItems + Reduce Stock
        for item in cart_items:
            design = item.design
            size = item.size
            qty = item.quantity

            size_entry = ProductColorSize.objects.select_for_update().filter(
                color=design.color,
                size=size
            ).first()

            if not size_entry:
                raise Exception(
                    f"Size {size} not available for {design.name}"
                )

            if size_entry.quantity < qty:
                raise Exception(
                    f"Insufficient stock for {design.name} ({size})"
                )

            OrderItem.objects.create(
                order=order,
                design=design,
                size=size,
                quantity=qty,
                price=Decimal(item.price)
            )

            # reduce stock
            size_entry.quantity -= qty
            size_entry.save()

        # ✅ Clear cart
        cart_items.delete()

    return order

@login_required
def start_phonepe_payment(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect("view_cart")

    total = sum(item.subtotal() for item in cart_items)
    merchant_order_id = f"FD_{uuid.uuid4().hex[:20]}"

    PaymentTransaction.objects.create(
        user=request.user,
        merchant_order_id=merchant_order_id,
        amount=total,
        status="PENDING"
    )

    # 1️⃣ Auth token
    token_res = requests.post(
        settings.PHONEPE_AUTH_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_id": settings.PHONEPE_CLIENT_ID,
            "client_version": settings.PHONEPE_CLIENT_VERSION,
            "client_secret": settings.PHONEPE_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    )

    token_data = token_res.json()
    if "access_token" not in token_data:
        return JsonResponse({"error": "PhonePe auth failed"}, status=400)

    access_token = token_data["access_token"]

    # 2️⃣ Create payment
    payload = {
        "merchantOrderId": merchant_order_id,
        "amount": int(total * 100),
        "paymentFlow": {
            "type": "PG_CHECKOUT",
            "merchantUrls": {
                "redirectUrl": settings.PHONEPE_REDIRECT_URL
            }
        }
    }

    pay_res = requests.post(
        settings.PHONEPE_PAY_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"O-Bearer {access_token}"
        },
        json=payload
    )

    res_data = pay_res.json()
    if "redirectUrl" not in res_data:
        return JsonResponse(res_data, status=400)

    return render(
        request,
        "phonepe_checkout.html",
        {"token_url": res_data["redirectUrl"]}
    )

import hashlib, base64
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
@csrf_exempt
def phonepe_webhook(request):
    # ===============================
    # 1️⃣ Verify PhonePe Authorization
    # ===============================
    auth_header = request.headers.get("Authorization")

    expected = "SHA256(" + hashlib.sha256(
        f"{settings.PHONEPE_WEBHOOK_USERNAME}:{settings.PHONEPE_WEBHOOK_PASSWORD}".encode()
    ).hexdigest() + ")"

    if auth_header != expected:
        # Unauthorized webhook
        return HttpResponse(status=401)

    # ===============================
    # 2️⃣ Parse payload
    # ===============================
    data = json.loads(request.body)
    event = data.get("event")
    payload = data.get("payload", {})

    merchant_order_id = payload.get("merchantOrderId")
    if not merchant_order_id:
        return HttpResponse(status=400)

    txn = PaymentTransaction.objects.filter(
        merchant_order_id=merchant_order_id
    ).first()

    if not txn:
        return HttpResponse(status=404)

    # ===============================
    # 3️⃣ Idempotency guard
    # ===============================
    if txn.status == "SUCCESS":
        return HttpResponse(status=200)

    # ===============================
    # 4️⃣ Handle events
    # ===============================
    if event == "checkout.order.completed":
        txn.status = "SUCCESS"
        txn.phonepe_order_id = payload.get("orderId")
        txn.save()

        create_order_from_cart(txn.user)

    elif event == "checkout.order.failed":
        txn.status = "FAILED"
        txn.save()

    return HttpResponse(status=200)


import time

@login_required
def phonepe_return(request):
    time.sleep(2)
    return redirect("orders") 