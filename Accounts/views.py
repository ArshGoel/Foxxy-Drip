from email.mime import message
from django.contrib.auth.models import User
from django.core.mail import send_mail
from Services.models import Product
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import CartItem
from django.contrib import auth,messages
from django.contrib.auth import authenticate, login as auth_login
from random import randint
from django.conf import settings
from .models import Profile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product, ProductDesign
# ------------------------ Clean Email ------------------------ #
def send_contact_email(name, email, message):
    subject = f"Foxxy Drip | New Contact Message from {name}"
    
    # Render HTML template
    html_content = render_to_string("emails/contact_email.html", {
        "name": name,
        "email": email,
        "message": message,
    })
    text_content = strip_tags(html_content)  # fallback plain text
    
    msg = EmailMultiAlternatives(
        subject,
        text_content,  # plain text
        email,  # from
        [settings.EMAIL_HOST_USER],  # to
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_forgot_password_email(name, email, otp):
    subject = f"Foxxy Drip | Forgot Password"
    
    # Render HTML template
    html_content = render_to_string("emails/forget_email.html", {
        "name": name,
        "email": email,
        "otp": otp,
    })
    text_content = strip_tags(html_content)  # fallback plain text

    msg = EmailMultiAlternatives(
        subject,
        text_content,  # plain text
        settings.EMAIL_HOST_USER,  # from
        [email],  # to
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_otp_email(name, email, otp):
    subject = f"Foxxy Drip | One-Time Password (OTP) Verification"
    
    # Render HTML template
    html_content = render_to_string("emails/otp_email.html", {
        "name": name,
        "email": email,
        "otp": otp,
    })
    text_content = strip_tags(html_content)  # fallback plain text

    msg = EmailMultiAlternatives(
        subject,
        text_content,  # plain text
        settings.EMAIL_HOST_USER,  # from
        [email],  # to
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# ------------------------ Clean Email ------------------------ #

# views.py
from django.shortcuts import render
from .models import ProductDesign
from django.shortcuts import render
from django.db.models import Prefetch, Case, When, IntegerField
from .models import Product, ProductColor, ProductDesign

# Define the desired type order
TYPE_ORDER = ['printed', 'plain', 'embroidery']
def all_products_designs_view(request):
    # Annotate designs with custom ordering
    custom_order = Case(
        *[When(type__type_name=t, then=pos) for pos, t in enumerate(TYPE_ORDER)],
        output_field=IntegerField()
    )

    # Prefetch designs for each color, ordering by type custom order
    color_qs = ProductColor.objects.prefetch_related(
        Prefetch(
            'designs',
            queryset=ProductDesign.objects.prefetch_related('images', 'type').order_by(custom_order)
        )
    )

    # Prefetch colors for each product
    products = Product.objects.prefetch_related(
        Prefetch('colors', queryset=color_qs)
    )

    context = {'products': products}
    return render(request, 'all_products_designs.html', context)

def home(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()

    # ✅ Fetch designs instead of products
    featured_designs = (
        ProductDesign.objects.filter(id__in=[2, 17, 15])
        .select_related("color__product", "type")
        .prefetch_related("images", "color__images", "color__product__images")
    )
    
    return render(request, "home.html", {
        "cart_count": cart_count,
        "featured_designs": featured_designs
    })


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

from Services.models import Product, ProductColor, ProductColorSize, ProductDesign, ProductImage

from django.shortcuts import render
from .models import Product

from django.db.models import Prefetch

def shop(request):
    # Prefetch colors, designs, images in a single query
    products = Product.objects.all().prefetch_related(
        Prefetch('colors', queryset=ProductColor.objects.prefetch_related(
            Prefetch(
                'designs',
                queryset=ProductDesign.objects.filter(show_in_shop=True).prefetch_related('images')  # 👈 only True designs
            ),
            'sizes',
            'images'
        ))
    )

    # Flatten each product per design for easier template rendering
    products_with_designs = []
    for product in products:
        for color in product.colors.all():  # type: ignore
            # If no (visible) designs, still show product+color
            if color.designs.exists():
                for design in color.designs.all():
                    products_with_designs.append({
                        "product": product,
                        "color": color,
                        "design": design,
                        "image": design.images.first() or color.images.first() or None
                    })
    return render(request, "shop.html", {"products_with_designs": products_with_designs})


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
            send_contact_email(name, email, message)
            
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contactus')  # Make sure this matches your URL name
        else:
            messages.error(request, "All fields are required.")

    return render(request, 'contactus.html', {'cart_count': cart_count})


def login(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")  # Check which form was submitted

        if form_type == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            if username and password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_superuser:
                        return redirect("verify", username=username)
                    else:
                        auth_login(request, user)
                        messages.success(request, "Login successful")
                        return redirect('/')
                else:
                    messages.error(request, "User Doesn't Exist")
                    
            return render(request, "login_register.html", {"username": username})

        elif form_type == "signup":
            username = request.POST.get("username")
            password = request.POST.get("password")
            email = request.POST.get("email")
            try:
                user = User.objects.create_user(username = username , password = password,email=email)
                user.save()
                auth.login(request ,user)

            except:
                messages.error(request,"Username Already exists")
                return render(request,"login_register.html",{"username":username,"email":email}) 
                
            messages.success(request,"Success")
        
    return render(request, 'login_register.html')



def logout(request):
    auth.logout(request)
    messages.success(request, "Logout successful")
    return redirect("login")

def profile(request):
    try:
        profile = request.user.profile
    except:
        return redirect("complete_profile")
    addresses = profile.addresses.all()
    wishlist_items = profile.wishlist_items.all()
    cart_items = request.user.cart_items.all()
    orders = profile.orders.all()

    # Check if user has a social account
    social_account = SocialAccount.objects.filter(user=request.user).first()
    login_method = social_account.provider if social_account else "username_password"

    return render(request, "profile.html", {
        "profile": profile,
        "addresses": addresses,
        "wishlist_items": wishlist_items,
        "cart_items": cart_items,
        "orders": orders,
        "login_method": login_method,
        "social_account": social_account,
    })

def verify(request,username):
    user = User.objects.get(username=username)
    otp = str(randint(100000, 999999))
    request.session['otp'] = otp
    try:
        email = user.email
        request.session['email_user'] = email  
        if not email:
            messages.error(request, "No email found for this user.")
            return render(request, "login_register.html", {"username": username})

        # Send the OTP to user's email
        send_otp_email(user.username, email, otp)

        request.session['otp'] = otp
        request.session['temp_user'] = username  
        messages.success(request, "OTP sent to your email.")
        return redirect("validate") 

    except Exception as e:
        print("Email error:", e)
        messages.error(request, "Failed to send OTP.")
        return render(request, "verify.html", {"username": username})
    
def mask_email(email):
    name, domain = email.split('@')
    visible = name[:4]
    masked = '*' * (len(name) - len(visible))
    return f"{visible}{masked}@{domain}"

def validate(request):
    session_email = request.session.get("email_user")
    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        username = request.session.get("temp_user")
        session_otp = request.session.get("otp")

        if not username or not otp_entered:
            messages.error(request, "Missing OTP or session expired.")
            return redirect("login")

        if otp_entered == session_otp:
            try:
                user = User.objects.get(username=username)
                auth_login(request, user)

                # Clean up session
                request.session.pop("otp", None)
                request.session.pop("temp_user", None)

                messages.success(request, "Login successful!")
                return redirect("/")

            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("login")
        else:
            messages.error(request, "Invalid OTP.")
            return render(request, "verify.html", {"username": username, "Type": "Voter"})
        
    masked_email = mask_email(session_email)
    return render(request, "verify.html", {"email": masked_email})

def forgetpass(request):
    stage = "request_otp"  # Initial stage
    email_masked = None

    if request.method == "POST":
        action = request.POST.get("action")

        # Stage 1: Request OTP
        if action == "send_otp":
            identifier = request.POST.get("identifier")

            user = User.objects.filter(username=identifier).first()
            if not user:
                user = User.objects.filter(email=identifier).first()

            if not user:
                messages.error(request, "User not found with that username or email.")
            elif not user.email:
                messages.error(request, "No email associated with this account.")
            else:
                otp = str(randint(100000, 999999))
                request.session['reset_otp'] = otp
                request.session['reset_user'] = user.username
                request.session['email_user'] = user.email

                send_forgot_password_email(user.username, user.email, otp)

                stage = "enter_otp"
                email_masked = mask_email(user.email)
                messages.success(request, f"OTP sent to your email: {email_masked}")

        # Stage 2: Validate OTP and Reset Password
        elif action == "reset_password":
            entered_otp = request.POST.get("otp")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            username = request.session.get("reset_user")
            session_otp = request.session.get("reset_otp")

            if not all([entered_otp, new_password, confirm_password]):
                messages.error(request, "All fields are required.")
                stage = "enter_otp"
            elif new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                stage = "enter_otp"
            elif entered_otp != session_otp:
                messages.error(request, "Invalid OTP.")
                stage = "enter_otp"
            else:
                try:
                    user = User.objects.get(username=username)
                    user.set_password(new_password)
                    user.save()
                    request.session.flush()
                    messages.success(request, "Password reset successful. Please login.")
                    return redirect("login")
                except User.DoesNotExist:
                    messages.error(request, "User not found.")
                    return redirect("forgetpass")

                stage = "request_otp"

    if request.session.get("email_user"):
        email_masked = mask_email(request.session.get("email_user"))
        stage = "enter_otp"

    return render(request, "forgetpass.html", {"stage": stage, "email_masked": email_masked})

@login_required
def complete_profile(request):
    # If profile already exists → redirect to manage_address
    if Profile.objects.filter(user=request.user).exists():
        return redirect("manage_address")

    if request.method == "POST":
        # profile_picture = request.FILES.get("profile_picture")  # will upload to Cloudinary automatically
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth") or None
        phone_number = request.POST.get("phone_number")
        firstname = request.POST.get("first_name")
        lastname = request.POST.get("last_name")
        user = request.user
        if firstname and lastname:
            user.first_name = firstname
            user.last_name = lastname
            user.save()

        # Create new profile
        Profile.objects.create(
            user=request.user,
            # profile_picture=profile_picture,
            gender=gender,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )

        messages.success(request, "Profile completed successfully!")
        return redirect("manage_address")

    return render(request, "complete_profile.html")

def privacy_policy(request, lang_code=None):
    context = {
        'initial_lang_code': lang_code if lang_code in ['en', 'hi', 'gu', 'ta', 'te', 'mr', 'ml', 'bn', 'kn', 'or'] else 'en'
    }
    return render(request, 'privacy_policy.html', context)

def terms_conditions(request, lang_code=None): 
    context = {
        'initial_lang_code': lang_code if lang_code in ['en', 'hi', 'gu', 'ta', 'te', 'mr', 'ml', 'bn', 'kn', 'or'] else 'en'
    }
    return render(request, 'terms_conditions.html', context)

def returns_and_exchanges_policy(request):
    return render(request, 'returns_exchange_policy.html')

def shipping_delivery_policy(request):
    return render(request, 'shipping_delivery_policy.html')