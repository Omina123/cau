from django.contrib import admin
from django.urls import path
from users import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('error_page', views.error_page, name= 'error_page'),
    path('Login', views.Login, name= 'Login'),
    path('register_user', views.register_user, name= 'register_user'),
    path('Logout/', views.Logout, name='Logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
    
    
    
    