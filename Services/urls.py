from django.urls import include, path
from Services import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', views.upload_product, name='upload_product'),
    path('', views.product_list, name='product_list'),
    path('edit/<str:product_id>/', views.edit_product, name='edit_product'),
    path('product/<str:product_id>/', views.view_product, name='view_product'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('dashboard/', views.dashboard, name='dashboard')
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  