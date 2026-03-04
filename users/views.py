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
            # Inside your Login view
            if user is not None:
                if not user.is_verified:
                    messages.error(request, "Please verify your email before logging in.")
                    request.session['verification_email'] = user.email
                    return redirect('verify_otp')
    
        
    # ... rest of your logic
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
# views.py
def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True # Or False if you want to block login until verified
            user.save()
            
            # Generate and Send OTP
            user.generate_otp()
            send_mail(
                'Verify your Parish Account',
                f'Your OTP for St. Peters Ngoisa is: {user.otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            
            # Redirect to the verification page
            request.session['verification_email'] = user.email
            return redirect('verify_otp') 
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

# views.py
def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        email = request.session.get('verification_email')
        
        try:
            user = CustomUser.objects.get(email=email, otp=otp_entered)
            user.is_verified = True
            user.otp = "" # Clear OTP after use
            user.save()
            messages.success(request, "Account verified! You can now login.")
            return redirect('Login')
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid OTP. Please try again.")
            
    return render(request, 'verify_otp.html')


# 1. This view handles the email submission form
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    # THIS LINE IS KEY: It tells Django to render the HTML properly
    html_email_template_name = 'password_reset_email.html' 
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