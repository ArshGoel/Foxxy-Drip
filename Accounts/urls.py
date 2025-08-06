from django.urls import include, path
from Accounts import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),
    path('FAQ',views.FAQ, name='FAQ'),
    path('aboutus',views.aboutus, name='aboutus'),
    path('contactus',views.contactus, name='contactus'),
    path('shop',views.shop, name='shop'),
    path('customize',views.customize, name='customize'),
    path("add/<str:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("view_cart", views.view_cart, name="view_cart"),
    path("remove/<str:product_id>/", views.remove_from_cart, name="remove_from_cart"),
]  +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
