from django.urls import include, path
from Services import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path("manage_address/",views.manage_address,name="manage_address"),
    path("delete_address/<int:address_id>/",views.delete_address,name="delete_address"),
    path('addresses/make-default/<int:address_id>/', views.make_default_address, name='make_default_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('upload/', views.upload_product, name='upload_product'),
    path('', views.product_list, name='product_list'),
    path('edit/<str:product_id>/', views.edit_product, name='edit_product'),
    path('product/<str:product_id>/', views.view_product, name='view_product'),
    path('wishlist', views.wishlist, name='wishlist'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  