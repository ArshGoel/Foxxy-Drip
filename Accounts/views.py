from django.contrib.auth import authenticate
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
    cart_items = {}

    if request.user.is_authenticated:
        cart = CartItem.objects.filter(user=request.user)
        for item in cart:
            cart_items[str(item.product.product_id)] = item.quantity  # use str key for safer template usage

    return render(request, 'shop.html', {
        'products': products,
        'cart_items': cart_items,
        'cart_count': cart_count,
    })

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
                user = User.objects.create_user(username = username , password = password)
                user.save()
                auth.login(request ,user)

            except:
                messages.error(request,"Username Already exists")
                return render(request,"login_register.html",{"username":username,"email":email}) 
                
            messages.success(request,"Success")
        
    return render(request, 'login_register.html')

def register(request):
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        try:
            user = User.objects.create_user(username = username , password = password)
            user.save()
            messages.success(request,"Registration Successful")
            return redirect('login')


        except:
            messages.error(request,"Username Already exists")
            return render(request,"login.html",{"username":username,"email":email}) 
            
    messages.success(request,"Success")
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    messages.success(request, "Logout successful")
    return redirect("login")

def profile(request):
    return render(request, 'profile.html')

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
        send_mail(
            subject="Your OTP for FOXXY DRIP Login",
            message=f"Hi {user.username},\n\nYour OTP for login is: {otp}",
            from_email=settings.EMAIL_HOST_USER,  # Must match your settings.EMAIL_HOST_USER
            recipient_list=[email],
            fail_silently=False,
        )

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

                send_mail(
                    subject="Password Reset OTP",
                    message=f"Hi {user.username},\n\nYour OTP for password reset is: {otp}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

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
        profile_picture = request.FILES.get("profile_picture")  # will upload to Cloudinary automatically
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth") or None
        phone_number = request.POST.get("phone_number")

        # Create new profile
        Profile.objects.create(
            user=request.user,
            profile_picture=profile_picture,
            gender=gender,
            date_of_birth=date_of_birth,
            phone_number=phone_number
        )

        messages.success(request, "Profile completed successfully!")
        return redirect("manage_address")

    return render(request, "complete_profile.html")