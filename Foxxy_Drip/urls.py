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
    path('FAQ',views.FAQ,name='FAQ'),
    path('contactus',views.contactus,name='contactus')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
