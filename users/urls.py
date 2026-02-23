from django.contrib import admin
from django.urls import path
from  Ngoiso import views
from users import views

urlpatterns = [
    path('error_page', views.error_page, name= 'error_page'),
    path('Login', views.Login, name= 'Login'),
    path('register_user', views.register_user, name= 'register_user'),
    path('Logout/', views.Logout, name='Logout'),

    
    
    
    ]