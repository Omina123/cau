import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_background_email(subject, recipient_email, template_name, context, plain_message=None):
    def run():
        try:
            html_content = render_to_string(template_name, context)
            text_content = plain_message if plain_message else strip_tags(html_content)
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
        except Exception as e:
            print(f"Email error: {e}") # Check Render logs for this

    threading.Thread(target=run).start()