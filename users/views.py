from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.http import HttpResponse

from .models import CustomUser
from .forms import LoginForm, UserRegisterForm
from .utils import send_brevo_email
from .EmailBackend import EmailBackend

# --- LOGIN / LOGOUT ---
def Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['Email']
            password = form.cleaned_data['password']
            user = EmailBackend.authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, "Login was successful")
                if user.is_superuser or user.user_type == '1':
                    return redirect('Dashbd')
                elif user.user_type == '2':
                    return redirect('StaffDashboard')
                elif user.user_type == '3':
                    return redirect('catechist_dashboard')
                return redirect('Dashbd')
            else:
                messages.error(request, "Invalid credentials")
                return redirect("error_page")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def Logout(request):
    logout(request)
    return redirect('Login')

def error_page(request):
    return render(request, "error.html", {"title": "Access Denied", "message": "Login required."})

# --- REGISTRATION & OTP ---
def register_user(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True 
            user.save()
            user.generate_otp()

            html_content = f"""
            <div style="font-family: Arial; padding: 20px;">
                <h2>Account Verification</h2>
                <p>Your OTP is: <strong style="font-size: 24px; color: #e74c3c;">{user.otp}</strong></p>
            </div>
            """
            send_brevo_email(user.email, "Verify Your Account", html_content)
            
            request.session['verification_email'] = user.email
            messages.success(request, "OTP sent to your email.")
            return redirect('verify_otp')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

# THIS IS THE FUNCTION YOUR ERROR WAS LOOKING FOR
def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        email = request.session.get('verification_email')
        
        try:
            user = CustomUser.objects.get(email=email, otp=otp_entered)
            user.is_verified = True
            user.otp = "" 
            user.save()
            messages.success(request, "Verified! You can now login.")
            return redirect('Login')
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid OTP.")
            
    return render(request, 'verify_otp.html')

# --- FORGOT PASSWORD (Using Brevo) ---
from django.template.loader import render_to_string
from django.utils import timezone

class CustomPasswordResetView(auth_views.PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        users = CustomUser.objects.filter(email=email)
        
        for user in users:
            # 1. Generate security credentials
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # 2. Prepare context for your styled template
            context = {
                'user': user,
                'protocol': 'https' if self.request.is_secure() else 'http',
                'domain': self.request.get_host(),
                'uid': uid,
                'token': token,
                'now': timezone.now(), # For the copyright year in footer
            }
            
            # 3. Render the styled HTML template
            html_content = render_to_string('password_reset_email.html', context)
            
            # 4. Send via Brevo
            send_brevo_email(
                to_email=user.email, 
                subject="Password Reset Request - St. Peters Parish", 
                html_content=html_content
            )

        # Redirect to the 'Done' page regardless of user existence (security best practice)
        return redirect(self.success_url)

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'