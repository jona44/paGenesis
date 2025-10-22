
from django.contrib import admin
from django.urls import include, path
from genesis.views import HtmxLoginView
from django.contrib.auth.views import LogoutView
from genesis import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('genesis.urls')),
    path('accounts/login/', HtmxLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
