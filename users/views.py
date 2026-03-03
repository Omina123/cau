from django.shortcuts import render,redirect
from  .models import *
from .forms import*
from .EmailBackend import EmailBackend
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from Ngoiso import views
from django.contrib.auth import logout
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

# Password Reset Views
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

def Logout(request):
    logout(request)
    return redirect('Login')

def error_page(request):
    title ="Access Denied"
    message= "You must login/Register to continue"
    context = {
         'title':title,
         'message':message
     }
    return render(request, "error.html", context)
def Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['Email']
            password = form.cleaned_data['password']
            user = EmailBackend.authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    messages.success(request, "Login was successful")
                    return redirect('Dashbd')
                if user.user_type == '1':
                    messages.success(request, "Login was successful")
                    return redirect('Dashbd')
                elif user.user_type == '2':
                    messages.success(request, "Login was successful")
                    return redirect('StaffDashboard')
                
                else:
                    return HttpResponse("error_page")
            else:
                messages.error(request, "User does not exist or invalid credentials")
                return redirect("error_page")
    else:
        # Return an empty form for GET requests
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

#user creation function
def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # signals will create Admin/Staff/Client automatically
            return redirect('Login')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})




# 1. This view handles the email submission form
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

# 2. This view shows the "Email Sent" success message
class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'

# 3. This view handles the actual password change via the secure link
class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

# 4. This view shows the final "Password Changed" message
class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'