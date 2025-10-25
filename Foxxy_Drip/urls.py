from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from Accounts import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Accounts.urls')),
    path('dash/', include('Services.urls')),
    path('',TemplateView.as_view(template_name = "home.html"), name='home'),
    path("accounts/",include("allauth.urls")),
    path('aboutus',views.aboutus,name='aboutus'),
    path('shop',views.shop,name='shop'),
    # path('FAQ',views.FAQ,name='FAQ'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('privacy-policy/<str:lang_code>/', views.privacy_policy, name='privacy_policy_lang'),
    path('terms-conditions',views.terms_conditions,name='terms_conditions'),
    path('returns-and-exchanges-policy',views.returns_and_exchanges_policy,name='returns_and_exchanges_policy'),
    path('shipping-delivery-policy',views.shipping_delivery_policy,name='shipping_delivery_policy'),
    path('contactus',views.contactus,name='contactus')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
