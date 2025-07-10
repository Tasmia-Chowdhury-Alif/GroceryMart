from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import RegistrationSerializer

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import redirect


def send_verification_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # user id

    confirm_link = request.build_absolute_uri(f"http://127.0.0.1:8000/accounts/activate/{uid}/{token}/")
    email_subject = "GroceryMart Account Varification"
    email_body = render_to_string(
        "accounts/verification_email.html", {"confirm_link": confirm_link}
    )

    email = EmailMultiAlternatives(email_subject, "", to=[user.email])
    email.attach_alternative(email_body, "text/html")
    email.send()

    return


# Create your views here.
class RegistrationViewSet(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(self.request, user)
        return Response(
            {"message": "Check your email to activate your account."},
            status=status.HTTP_201_CREATED,
        )


def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()  # user id
        user = User._default_manager.get(pk=uid)
    except User.DoesNotExist:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("registration")
    else:
        print("Invalid credentials")
        return redirect("registration")
