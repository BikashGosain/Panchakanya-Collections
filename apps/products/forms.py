from django import forms
from django.forms import inlineformset_factory

from .models import Category, Product, ProductImage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "description",
            "category",
            "metal_type",
            "purity",
            "weight_grams",
            "price",
            "stock",
            "status",
            "featured",
        ]


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=["image", "is_primary"],
    extra=1,
    can_delete=True,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "parent", "image", "show_on_home"]
