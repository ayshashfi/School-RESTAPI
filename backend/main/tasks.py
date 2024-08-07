
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model



@shared_task(bind=True)
def test_func(self):
    return "Done"


@shared_task
def send_password_set_email(user_id):
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
        email = user.email
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = 'http://127.0.0.1:8000/'  # Update to your production site URL
        mail_subject = "Reset your password"

        link = f'{current_site}create-new-password/?uid={uid}&token={token}'
        print(link, 'link---------')

        context = {
            "link": link,
            "username": user.username
        }
        subject = "Password reset email"
        html_body = render_to_string("email/set_password.html", context)
        email_message = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[email]
        )
    
        email_message.content_subtype = 'html'
        email_message.send(fail_silently=False)
        print("done")
    except User.DoesNotExist:
        print(f"User with id {user_id} does not exist.")