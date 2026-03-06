from .models import *
from django.contrib.auth.forms import UserCreationForm
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

#creatng authentication form
class FogotForm(forms.Form):
    email= forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
class LoginForm(forms.Form):
    Email = forms.CharField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))

# users/forms.py
from django import forms
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from users.utils import send_async_email

class PasswordResetForm(DjangoPasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        # Render email as usual
        subject = self.get_subject(subject_template_name, context)
        body = self.get_email_body(email_template_name, context)
        html_message = self.get_email_body(html_email_template_name, context) if html_email_template_name else None

        send_async_email(subject, body, [to_email], html_message=html_message)
class UserRegisterForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register'))