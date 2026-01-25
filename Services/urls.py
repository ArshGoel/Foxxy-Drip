from django.urls import include, path
from Services import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("manage_address/",views.manage_address,name="manage_address"),
    path("delete_address/<int:address_id>/",views.delete_address,name="delete_address"),
    path('addresses/make-default/<int:address_id>/', views.make_default_address, name='make_default_address'),
    path('addresses/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('view_cart', views.view_cart, name='view_cart'),
    path("cart/update/<int:item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    path("cart/remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/", views.checkout, name="checkout"), 
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/", views.orders, name="orders"),

    path("admin/orders/", views.admin_orders_list, name="admin_orders_list"), 
    path("admin/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin/orders/<int:order_id>/update/", views.admin_update_order_status, name="admin_update_order_status"), #type:ignore
    path("download_backup/", views.download_backup, name="download_backup"),

    path("payment_page/", views.payment_page, name="payment_page"),

    path("sessions/", views.active_sessions, name="active_sessions"),
    path("sessions/logout/<str:session_key>/", views.logout_other_session, name="logout_other_session"),
]