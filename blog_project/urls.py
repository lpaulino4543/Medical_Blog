from django.contrib import admin
from django.urls import path, include
from blog.views import home, profile
from blog.views import register
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('blog', profile),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    
]