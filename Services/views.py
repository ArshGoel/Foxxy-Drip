from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
import json

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