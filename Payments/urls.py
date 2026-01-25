from django.urls import include, path
from Payments import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("phonepe/start/",views.start_phonepe_payment,name="start_phonepe_payment"),
    path("phonepe/webhook/",views.phonepe_webhook,name="phonepe_webhook"),
    path("phonepe/return/",views.phonepe_return,name="phonepe_return"),
] 