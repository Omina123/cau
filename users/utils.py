# users/utils.py
import threading
from django.core.mail import send_mail
from django.conf import settings

def send_async_email(subject, message, recipient_list, html_message=None):
    """
    Sends email in a separate thread to prevent blocking the request.
    """
    def _send():
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )
    threading.Thread(target=_send).start()