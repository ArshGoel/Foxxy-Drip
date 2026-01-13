from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_form, name="category_add"),
    path("categories/<int:pk>/edit/", views.category_form, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    path("products/", views.product_list, name="product_list"),
    path("products/add/", views.product_form, name="product_add"),
    path("products/<str:pk>/edit/", views.product_form, name="product_edit"),

    path("types/", views.type_list, name="type_list"),
    path("types/add/", views.type_form, name="type_add"),
    path("types/<int:pk>/edit/", views.type_form, name="type_edit"),

    path("colors/", views.color_list, name="color_list"),
    path("colors/add/", views.color_form, name="color_add"),

    path("sizes/", views.size_list, name="size_list"),
    path("sizes/add/", views.size_form, name="size_add"),

    path("images/", views.image_list, name="image_list"),
    path("images/add/", views.image_form, name="image_add"),
    path("colors/<int:pk>/edit/", views.color_form, name="color_edit"),

# Sizes
    path("sizes/<int:pk>/edit/", views.size_form, name="size_edit"),

    # Images
    path("images/<int:pk>/edit/", views.image_form, name="image_edit"),
    path("products/add-full/", views.product_full_create, name="product_full_create"),      

]
