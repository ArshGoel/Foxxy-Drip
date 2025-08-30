from django.urls import include, path
from Accounts import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login',views.login,name="login"),
    # path('FAQ',views.FAQ, name='FAQ'),
    # path('aboutus',views.aboutus, name='aboutus'),
    # path('contactus',views.contactus, name='contactus'),
    path('customize',views.customize, name='customize'),
    path('logout',views.logout,name="logout"), 
    path('profile', views.profile, name='profile'),
    path('forgetpass', views.forgetpass, name='forgetpass'),
    path('verify/<str:username>/', views.verify, name='verify'),
    path('validate', views.validate, name='validate'),
    path('complete_profile', views.complete_profile, name='complete_profile'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
