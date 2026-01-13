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
    form = ProductImageForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("image_list")
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

            # ---------------- IMAGES ----------------
            for img in request.FILES.getlist("images"):
                ProductImage.objects.create(
                    product=product,
                    product_type=product_type,
                    color=color,
                    image=img,
                )

            return redirect("product_list")

        except Exception as e:
            context["error"] = str(e)

    return render(request, "admin_d/product_full_create.html", context)
