from django import forms
from .models import (
    Category, Product, ProductType,
    ProductColor, ProductColorSize, ProductImage
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class ProductTypeForm(forms.ModelForm):
    class Meta:
        model = ProductType
        fields = "__all__"


class ProductColorForm(forms.ModelForm):
    class Meta:
        model = ProductColor
        fields = "__all__"


class ProductColorSizeForm(forms.ModelForm):
    class Meta:
        model = ProductColorSize
        fields = "__all__"


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = "__all__"


from django import forms
from .models import (
    Product, ProductType,
    ProductColor, ProductColorSize,
    ProductImage
)

class FullProductCreateForm(forms.Form):
    # Product
    product_id = forms.CharField(max_length=20)
    product_name = forms.CharField(max_length=100)
    category = forms.ModelChoiceField(queryset=None)

    # Type
    type_name = forms.ChoiceField(choices=ProductType.TYPE_CHOICES)
    price = forms.DecimalField()
    discount_price = forms.DecimalField(required=False)

    # Color
    color_name = forms.CharField(max_length=50)

    # Size + Stock
    size = forms.ChoiceField(choices=ProductColorSize.SIZE_CHOICES)
    quantity = forms.IntegerField(min_value=0)

    # Image
    image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        from .models import Category
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all() #type: ignore
