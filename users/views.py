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
                if user.user_type == '1':
                    messages.success(request, "Login was successful")
                    return redirect('Dashbd')
                elif user.user_type == '2':
                    messages.success(request, "staff logged in")
                    return redirect('')
                
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