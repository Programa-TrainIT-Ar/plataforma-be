from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializer import UsersSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import jwt

from authlib.integrations.django_client import OAuth
from django.urls import reverse
from rest_framework.views import APIView
from datetime import timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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



# Vista para iniciar sesión a través de Auth0
class Auth0LoginView(APIView):
    def get(self, request):
        return oauth.auth0.authorize_redirect(
            request, request.build_absolute_uri(reverse("auth0_callback"))
        )

# Vista para manejar el callback de Auth0 después de iniciar sesión
class Auth0CallbackView(APIView):
    def get(self, request):
        token = oauth.auth0.authorize_access_token(request)
        user_info = oauth.auth0.parse_id_token(request, token)
        user_email = user_info.get("email")

        User = get_user_model()
        try:
            usuario = User.objects.get(email=user_email)
        except User.DoesNotExist:
            # Crear un nuevo usuario si no existe en la base de datos local
            usuario = User.objects.create(
                username=user_email.split("@")[0],
                email=user_email,
                is_active=True,
            )

        # Generar tokens de acceso y refresco para el usuario
        refresh = RefreshToken.for_user(usuario)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': usuario.id
        }, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    serializer_class = UsersSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)

        #genera el token
        token= RefreshToken.for_user(user).access_token
        token.set_exp(lifetime=timedelta(hours=1))

        #genera url
        activation_url= request.build_absolute_uri(reverse('activate',kwargs={'token':str(token)}))


        #renderizar HTML
        html_message = render_to_string('email/activation_email.html', {'activation_url': activation_url})
        plain_message = strip_tags(html_message)


        send_mail(
            'Activacion de cuenta',
            plain_message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )

        return Response(
           { "detail": "Cuenta registrada. Revisa tu correo para activar tu cuenta."}, status=status.HTTP_201_CREATED
         )


class ActivationView(generics.GenericAPIView):
        def post(self, request, token):
            try:
               
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = get_user_model()
                users=user.objects.get(id=payload['user_id'])

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
                return Response({'message': 'Token expirado'}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.JWTError:
                return Response({'message': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
            except user.DoesNotExist:
                return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
            

class LoginView(generics.GenericAPIView):
    serializer_class = UsersSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = get_user_model()
        users = user.objects.filter(email=email).first()

        if users and users.check_password(password):
            if not users.is_active:
                return Response({"error": "Cuenta no activa. contacte al administrador"}, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(users)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': users.id
            })

        else:
            return Response({"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED)
        

class PerfilView(generics.RetrieveAPIView):
    serializer_class = UsersSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        users = request.user
        serializer = self.get_serializer(users)
        return Response(serializer.data)
    
            