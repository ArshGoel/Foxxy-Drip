from django.urls import include, path
from Services import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("manage_address/",views.manage_address,name="manage_address"),
    path("delete_address/<int:address_id>/",views.delete_address,name="delete_address"),
    path('addresses/make-default/<int:address_id>/', views.make_default_address, name='make_default_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),

    path('upload/', views.upload_product, name='upload_product'),
    path('', views.product_list, name='product_list'),
    path('edit/<str:product_id>/', views.edit_product, name='edit_product'),
    path('dash/<str:product_id>/designs/', views.product_designs_view, name='product_designs'),
    path('product/<str:pk>/', views.view_product, name='view_product'),
    path('wishlist', views.wishlist, name='wishlist'),
    path('view_products', views.view_products, name='view_products'),
    path('view_cart', views.view_cart, name='view_cart'),
    path("cart/update/<int:item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("cart/remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/", views.checkout, name="checkout"), 
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/", views.orders, name="orders"),
    path("add-to-cart/<int:design_id>/", views.add_to_cart, name="add_to_cart"),#type:ignore

    path("admin/orders/", views.admin_orders_list, name="admin_orders_list"), 
    path("admin/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin/orders/<int:order_id>/update/", views.admin_update_order_status, name="admin_update_order_status"), #type:ignore
    path("download_backup/", views.download_backup, name="download_backup"),

    path("payment_page/", views.payment_page, name="payment_page"),

    path("design/<int:design_id>/", views.design_detail, name="design_detail"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  