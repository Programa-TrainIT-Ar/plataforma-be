import logging
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from .models import Usuario
from .serializer import (
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UsersSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import jwt
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from authlib.integrations.django_client import OAuth
from django.urls import reverse
from rest_framework.views import APIView
from datetime import timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)


class Auth0LoginView(APIView):
    def get(self, request):
        return oauth.auth0.authorize_redirect(
            request, request.build_absolute_uri(reverse("auth0_callback"))
        )


class Auth0CallbackView(APIView):
    def get(self, request):
        token = oauth.auth0.authorize_access_token(request)
        user_info = oauth.auth0.parse_id_token(request, token)
        user_email = user_info.get("email")

        User = get_user_model()
        try:
            usuario = User.objects.get(email=user_email)
        except User.DoesNotExist:
            usuario = User.objects.create(
                username=user_email.split("@")[0],
                email=user_email,
                is_active=True,
            )

        refresh = RefreshToken.for_user(usuario)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": usuario.id,
            },
            status=status.HTTP_200_OK,
        )


class RegisterView(generics.CreateAPIView):
    serializer_class = UsersSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)

        token = RefreshToken.for_user(user).access_token
        token.set_exp(lifetime=timedelta(hours=1))

        activation_url = request.build_absolute_uri(
            reverse("activate", kwargs={"token": str(token)})
        )

        html_message = render_to_string(
            "email/activation_email.html", {"activation_url": activation_url}
        )
        plain_message = strip_tags(html_message)

        send_mail(
            "Activacion de cuenta",
            plain_message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Cuenta registrada. Revisa tu correo para activar tu cuenta."},
            status=status.HTTP_201_CREATED,
        )


class ActivationView(generics.GenericAPIView):
    def post(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = get_user_model()
            users = user.objects.get(id=payload["user_id"])

            if not users.is_active:
                users.is_active = True
                users.save()
                return Response(
                    {"mensaje": "Usuario activado correctamente."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "El usuario ya está activado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except jwt.ExpiredSignatureError:
            return Response(
                {"message": "Token expirado"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.JWTError:
            return Response(
                {"message": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST
            )
        except user.DoesNotExist:
            return Response(
                {"message": "Usuario no encontrado"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(generics.GenericAPIView):
    serializer_class = UsersSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = get_user_model()
        users = user.objects.filter(email=email).first()

        if users and users.check_password(password):
            if not users.is_active:
                return Response(
                    {"error": "Cuenta no activa. contacte al administrador"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refresh = RefreshToken.for_user(users)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": users.id,
                }
            )
        else:
            return Response(
                {"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED
            )


class PerfilView(generics.RetrieveAPIView):
    serializer_class = UsersSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = request.user
        serializer = self.get_serializer(users)
        return Response(serializer.data)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UsersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id=None, *args, **kwargs):
        User = get_user_model()
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "Usuario no encontrado"}, status=404)
        else:
            user = request.user

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=200)


class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            # Check if the email exists in the database
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return Response(
                    {"error": "No existe un usuario con ese correo electrónico."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Rate limiting
            cache_key = f"password_reset_{user.id}"
            last_request = cache.get(cache_key)

            if (
                last_request and (timezone.now() - last_request).total_seconds() < 300
            ):  # 5 minutes
                return Response(
                    {
                        "error": "Por favor, espere 5 minutos antes de solicitar otro restablecimiento de contraseña."
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Update last request time
            cache.set(cache_key, timezone.now(), 300)  # Store for 5 minutes

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            domain = (
                "localhost:8000"  
            )
            reset_link = f"http://{domain}/api/usuarios/reset-password/{uid}/{token}/"

            mail_subject = "Restablecimiento de contraseña"
            html_message = render_to_string(
                "email/reset_password_email.html",
                {"user": user, "reset_link": reset_link},
            )
            plain_message = strip_tags(html_message)

            send_mail(
                mail_subject,
                plain_message,
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Reset password link sent: {reset_link}")

            return Response(
                {"message": "Se ha enviado un correo para restablecer la contraseña."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            logger.error(f"Invalid uidb64: {uidb64}")
            return Response(
                {"error": "Token inválido o usuario no encontrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            logger.error(f"Invalid token for user {user.id}: {token}")
            return Response(
                {"error": "Token inválido o expirado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(
                {"message": "Contraseña restablecida exitosamente."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
