from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
def category_list(request):
    return render(request, "admin_d/category_list.html", {
        "categories": Category.objects.all()
    })

def category_form(request, pk=None):
    obj = Category.objects.get(pk=pk) if pk else None
    form = CategoryForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("category_list")
    return render(request, "admin_d/category_form.html", {"form": form})

def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("category_list")
    return render(request, "admin_d/confirm_delete.html", {"object": obj})
def product_list(request):
    return render(request, "admin_d/product_list.html", {
        "products": Product.objects.select_related("category")
    })

def product_form(request, pk=None):
    obj = Product.objects.get(pk=pk) if pk else None
    form = ProductForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("product_list") 
    return render(request, "admin_d/product_form.html", {"form": form})
def type_list(request):
    return render(request, "admin_d/type_list.html", {
        "types": ProductType.objects.select_related("product")
    })

def type_form(request, pk=None):
    obj = ProductType.objects.get(pk=pk) if pk else None
    form = ProductTypeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("type_list")
    return render(request, "admin_d/type_form.html", {"form": form})
def color_list(request):
    return render(request, "admin_d/color_list.html", {
        "colors": ProductColor.objects.select_related("product")
    })

def color_form(request, pk=None):
    obj = ProductColor.objects.get(pk=pk) if pk else None
    form = ProductColorForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("color_list")
    return render(request, "admin_d/color_form.html", {"form": form})
def size_list(request):
    return render(request, "admin_d/size_list.html", {
        "sizes": ProductColorSize.objects.select_related("color")
    })

def size_form(request, pk=None):
    obj = ProductColorSize.objects.get(pk=pk) if pk else None
    form = ProductColorSizeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("size_list")
    return render(request, "admin_d/size_form.html", {"form": form})
def image_list(request):
    return render(request, "admin_d/image_list.html", {
        "images": ProductImage.objects.select_related("product")
    })

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
 
from django.db import transaction
from django.shortcuts import render, redirect
from .models import *

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

from django.shortcuts import render
from .models import Design, ProductImage

def shop(request):
    designs = (
        Design.objects
        .filter(show_in_shop=True)
        .select_related("product", "product_type", "color")
        .prefetch_related("images")
    )

    # attach primary image to each design
    for d in designs:
        d.primary_image = d.images.filter(is_primary=True).first() or d.images.first()
        d.sizes = ProductColorSize.objects.filter(color=d.color).order_by("size")
    return render(request, "user/shop.html", {"designs": designs})

 
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from .models import Product, ProductType, ProductColor, ProductColorSize, ProductImage

from django.shortcuts import render, get_object_or_404
from .models import Product, ProductType, ProductColor, ProductColorSize, Design, ProductImage

def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    types = ProductType.objects.filter(product=product)
    colors = ProductColor.objects.filter(product=product)

    selected_type_id = request.GET.get("type")
    selected_color_id = request.GET.get("color")
    selected_design_id = request.GET.get("design")  # ✅ NEW

    selected_type = (
        ProductType.objects.filter(id=selected_type_id, product=product).first()
        if selected_type_id else None
    )
    selected_color = (
        ProductColor.objects.filter(id=selected_color_id, product=product).first()
        if selected_color_id else None
    )

    # ✅ defaults
    if not selected_type:
        selected_type = types.first()

    if not selected_color:
        selected_color = colors.first()

    # ✅ Stock sizes (still based on color)
    sizes = []
    if selected_color:
        sizes = ProductColorSize.objects.filter(color=selected_color).order_by("size")

    # ✅ ALL designs for current selection
    designs = Design.objects.none()
    if selected_type and selected_color:
        designs = (
            Design.objects.filter(
                product=product,
                product_type=selected_type,
                color=selected_color,
                show_in_shop=True   # ✅ optional: only show visible designs
            )
            .order_by("position", "-id")
        )

    # ✅ choose 1 design (by design id if present)
    design = None

    if selected_design_id:
        design = designs.filter(id=selected_design_id).first()

    # ✅ fallback = first design
    if not design:
        design = designs.first()

    # ✅ Images from design
    images = ProductImage.objects.none()
    primary_image = None

    if design:
        images = ProductImage.objects.filter(design=design).order_by("-is_primary", "id")
        primary_image = images.first()

    return render(request, "user/product_detail.html", {
        "product": product,
        "types": types,
        "colors": colors,

        "selected_type": selected_type,
        "selected_color": selected_color,
        "sizes": sizes,
        "designs": designs,
        "design": design,

        "images": images,
        "primary_image": primary_image,
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Design
from .forms import DesignForm

def design_list(request):
    designs = Design.objects.select_related("product", "product_type", "color").prefetch_related("images")
    return render(request, "admin_d/design_list.html", {"designs": designs})


from django.shortcuts import render, redirect
from .models import Design, ProductImage
from .forms import DesignForm

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



from django.shortcuts import render, redirect, get_object_or_404
from .models import Design

def design_reorder(request):
    designs = Design.objects.all().order_by("position", "id")
    return render(request, "admin_d/design_reorder.html", {"designs": designs})

def move_design_up(request, pk):
    design = get_object_or_404(Design, pk=pk)
    above = Design.objects.filter(position__lt=design.position).order_by("-position").first()

    if above:
        design.position, above.position = above.position, design.position
        design.save()
        above.save()

    return redirect("design_reorder")

def move_design_down(request, pk):
    design = get_object_or_404(Design, pk=pk)
    below = Design.objects.filter(position__gt=design.position).order_by("position").first()

    if below:
        design.position, below.position = below.position, design.position
        design.save()
        below.save()

    return redirect("design_reorder")