from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.db import transaction
from .models import Product, ProductType, ProductColor, ProductColorSize, Design, ProductImage
from .forms import DesignForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Accounts.models import Wishlist, Profile
from django.views.decorators.http import require_POST
from Products.models import Design, ProductColorSize
from Accounts.models import CartItem
from django.contrib import messages

#admin methods
@staff_member_required
def category_list(request):
    return render(request, "admin_d/category_list.html", {
        "categories": Category.objects.all()
    })

@staff_member_required
def category_form(request, pk=None):
    obj = Category.objects.get(pk=pk) if pk else None
    form = CategoryForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("category_list")
    return render(request, "admin_d/category_form.html", {"form": form})

@staff_member_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("category_list")
    return render(request, "admin_d/confirm_delete.html", {"object": obj})

@staff_member_required
def product_list(request):
    return render(request, "admin_d/product_list.html", {
        "products": Product.objects.select_related("category")
    })

@staff_member_required
def product_form(request, pk=None):
    obj = Product.objects.get(pk=pk) if pk else None
    form = ProductForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("product_list") 
    return render(request, "admin_d/product_form.html", {"form": form})

@staff_member_required
def type_list(request):
    return render(request, "admin_d/type_list.html", {
        "types": ProductType.objects.select_related("product")
    })

@staff_member_required
def type_form(request, pk=None):
    obj = ProductType.objects.get(pk=pk) if pk else None
    form = ProductTypeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("type_list")
    return render(request, "admin_d/type_form.html", {"form": form})

@staff_member_required
def color_list(request):
    return render(request, "admin_d/color_list.html", {
        "colors": ProductColor.objects.select_related("product")
    })

@staff_member_required
def color_form(request, pk=None):
    obj = ProductColor.objects.get(pk=pk) if pk else None
    form = ProductColorForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("color_list")
    return render(request, "admin_d/color_form.html", {"form": form})

@staff_member_required
def size_list(request):
    return render(request, "admin_d/size_list.html", {
        "sizes": ProductColorSize.objects.select_related("color")
    })

@staff_member_required
def size_form(request, pk=None):
    obj = ProductColorSize.objects.get(pk=pk) if pk else None
    form = ProductColorSizeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("size_list")
    return render(request, "admin_d/size_form.html", {"form": form})

@staff_member_required
def image_list(request):
    return render(request, "admin_d/image_list.html", {
        "images": ProductImage.objects.select_related("product")
    })

@staff_member_required
def image_form(request, pk=None):
    obj = ProductImage.objects.get(pk=pk) if pk else None

    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("image_list")
    else:
        form = ProductImageForm(instance=obj)

    return render(request, "admin_d/image_form.html", {"form": form})
 
@staff_member_required
@transaction.atomic
def product_full_create(request):
    context = {
        "categories": Category.objects.all(),
        "products": Product.objects.all(),
        "types": ProductType.objects.all(),
        "colors": ProductColor.objects.all(),
    }

    if request.method == "POST":
        try:
            # ---------------- PRODUCT ----------------
            if request.POST.get("product_mode") == "existing":
                product = Product.objects.get(
                    product_id=request.POST["product_existing"]
                )
            else:
                product = Product.objects.create(
                    product_id=request.POST["product_id"],
                    name=request.POST["product_name"],
                    category_id=request.POST["category"],
                )

            # ---------------- PRODUCT TYPE ----------------
            if request.POST.get("type_mode") == "existing":
                product_type = ProductType.objects.get(
                    id=request.POST["type_existing"]
                )
            else:
                product_type = ProductType.objects.create(
                    product=product,
                    type_name=request.POST["type_name"],
                    price=request.POST["price"],
                    discount_price=request.POST.get("discount_price") or None,
                )

            # ---------------- COLOR ----------------
            if request.POST.get("color_mode") == "existing":
                color = ProductColor.objects.get(
                    id=request.POST["color_existing"]
                )
            else:
                color = ProductColor.objects.create(
                    product=product,
                    name=request.POST["color_name"]
                )

            # ---------------- SIZES ----------------
            sizes = request.POST.getlist("size[]")
            quantities = request.POST.getlist("quantity[]")

            for s, q in zip(sizes, quantities):
                ProductColorSize.objects.create(
                    color=color,
                    size=s,
                    quantity=int(q)
                )

            show_in_shop = True if request.POST.get("show_in_shop") else False
            description = request.POST.get("description")

            images = request.FILES.getlist("images")

            for i, img in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    product_type=product_type,
                    color=color,
                    image=img,
                    is_primary=(i == 0),   # ✅ first image primary
                    show_in_shop=show_in_shop,
                    description=description
                )


            return redirect("product_list")

        except Exception as e:
            context["error"] = str(e)

    return render(request, "admin_d/product_full_create.html", context)

@staff_member_required
def design_list(request):
    designs = Design.objects.select_related("product", "product_type", "color").prefetch_related("images")
    return render(request, "admin_d/design_list.html", {"designs": designs})

@staff_member_required
def design_form(request, pk=None):
    obj = Design.objects.get(pk=pk) if pk else None
    form = DesignForm(request.POST or None, instance=obj)

    if request.method == "POST":
        if form.is_valid():
            design = form.save()

            # ✅ handle images upload
            images = request.FILES.getlist("images")

            # if design has no primary yet, first upload becomes primary
            has_primary = ProductImage.objects.filter(design=design, is_primary=True).exists()

            for i, img in enumerate(images):
                ProductImage.objects.create(
                    design=design,
                    image=img,
                    is_primary=(not has_primary and i == 0)
                )

            return redirect("design_list")

    return render(request, "admin_d/design_form.html", {"form": form})

@staff_member_required
def design_reorder(request):
    designs = Design.objects.all().order_by("position", "id")
    return render(request, "admin_d/design_reorder.html", {"designs": designs})

@staff_member_required
def move_design_up(request, pk):
    design = get_object_or_404(Design, pk=pk)
    above = Design.objects.filter(position__lt=design.position).order_by("-position").first()

    if above:
        design.position, above.position = above.position, design.position
        design.save()
        above.save()

    return redirect("design_reorder")

@staff_member_required
def move_design_down(request, pk):
    design = get_object_or_404(Design, pk=pk)
    below = Design.objects.filter(position__gt=design.position).order_by("position").first()

    if below:
        design.position, below.position = below.position, design.position
        design.save()
        below.save()

    return redirect("design_reorder")


#user methods
def shop(request):
    designs = (
        Design.objects.filter(show_in_shop=True)
        .select_related("product", "product_type", "color")
        .prefetch_related("images")
    )

    for d in designs:
        d.primary_image = d.images.filter(is_primary=True).first() or d.images.first()
        d.sizes = ProductColorSize.objects.filter(color=d.color).order_by("size")

    wishlist_product_ids = set()
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            wishlist_product_ids = set(
                Wishlist.objects.filter(user=profile).values_list("design_id", flat=True)
            )

    return render(request, "user/shop.html", {
        "designs": designs,
        "wishlist_product_ids": wishlist_product_ids
    })

@login_required
def toggle_wishlist(request, design_id):
    profile = get_object_or_404(Profile, user=request.user)
    design = get_object_or_404(Design, id=design_id)

    obj = Wishlist.objects.filter(user=profile, design=design).first()

    if obj:
        obj.delete()
    else:
        Wishlist.objects.create(user=profile, design=design)

    return redirect(request.META.get("HTTP_REFERER", "shop"))

def design_detail(request, design_id):
    design = get_object_or_404(
        Design.objects.select_related("product", "product_type", "color"),
        id=design_id,
        show_in_shop=True
    )

    product = design.product

    # ✅ show all types/colors for switching
    types = ProductType.objects.filter(product=product)
    colors = ProductColor.objects.filter(product=product)

    selected_type = design.product_type
    selected_color = design.color

    # ✅ Sizes stock (color based)
    sizes = ProductColorSize.objects.filter(color=selected_color).order_by("size")

    # ✅ all designs for current product + selected type + color
    designs = (
        Design.objects.filter(
            product=product,
            product_type=selected_type,
            color=selected_color,
            show_in_shop=True
        )
        .order_by("position", "-id")
    )

    # ✅ Images of THIS design
    images = design.images.all().order_by("-is_primary", "id")
    primary_image = images.filter(is_primary=True).first() or images.first()

    return render(request, "user/design_detail.html", {
        "product": product,
        "types": types,
        "colors": colors,
        "sizes": sizes,

        "designs": designs,     # for design switching if you want
        "design": design,       # main design
        "selected_type": selected_type,
        "selected_color": selected_color,

        "images": images,
        "primary_image": primary_image,
    })
 
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@require_POST
@login_required
def add_to_cart(request):
    design_id = request.POST.get("design_id")
    size = request.POST.get("size")
    qty = request.POST.get("quantity")

    # ✅ redirect back to same page
    redirect_url = request.META.get("HTTP_REFERER", "/")

    if not design_id or not size or not qty:
        messages.error(request, "Missing fields ❌")
        return redirect(redirect_url)

    try:
        qty = int(qty)
        if qty <= 0:
            messages.error(request, "Quantity must be >= 1 ❌")
            return redirect(redirect_url)
    except:
        messages.error(request, "Invalid quantity ❌")
        return redirect(redirect_url)

    design = get_object_or_404(Design, id=design_id)

    # ✅ Stock check
    stock = ProductColorSize.objects.filter(color=design.color, size=size).first()

    if not stock:
        messages.error(request, "Size not available ❌")
        return redirect(redirect_url)

    if stock.quantity < qty:
        messages.error(request, f"Only {stock.quantity} left in stock ❌")
        return redirect(redirect_url)

    # ✅ Add/update cart
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        design=design,
        size=size,
        defaults={"quantity": qty}
    )

    if not created:
        cart_item.quantity += qty
        cart_item.save()

    messages.success(request, "Added to cart ✅")
    return redirect("view_cart")
