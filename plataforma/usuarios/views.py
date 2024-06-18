from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializers import UsuarioSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import jwt
#from .models import Usuario
from authlib.integrations.django_client import OAuth
from django.urls import reverse
from rest_framework.views import APIView
from datetime import  timedelta

# Configurar OAuth con Auth0 utilizando Authlib
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
'''El "callback" en el contexto de la integración con OAuth y servicios de autenticación 
como Auth0 se refiere a una URL a la cual el proveedor de identidad (en este caso, Auth0) 
redirige al usuario después de que este ha completado un proceso de autenticación exitoso.'''
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

# Vista para el registro de nuevos usuarios
class RegistroView(generics.CreateAPIView):
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save(is_active=False)  # El usuario no está activo inicialmente

        # Generar el token de activación
        token = RefreshToken.for_user(usuario).access_token
        # Configurar la expiración del token
        token.set_exp(lifetime=timedelta(hours=1))

        # Generar la URL de activación
        activation_url = request.build_absolute_uri(
            reverse('activate', kwargs={'token': str(token)})
        )

        # Enviar el correo de activación
        send_mail(
            'Activación de cuenta',
            f'Gracias por registrarse en TrainIT. Use el siguiente enlace para activar su cuenta: {activation_url}',
            settings.EMAIL_HOST_USER,
            [usuario.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Registro exitoso. Por favor, revise su correo para activar su cuenta."},
            status=status.HTTP_201_CREATED
        )

# Vista para activar un usuario mediante un token de activación
class ActivarView(generics.GenericAPIView):
    def get(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            User = get_user_model()
            usuario = User.objects.get(id=payload["user_id"])

            if not usuario.is_active:
                usuario.is_active = True
                usuario.save()
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
                {"error": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.JWTError:
            return Response(
                {"error": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

# Vista para iniciar sesión de usuarios locales
class IniciarSesionView(generics.GenericAPIView):
    serializer_class = UsuarioSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        User = get_user_model()
        usuario = User.objects.filter(email=email).first()

        if usuario and usuario.check_password(password):
            if not usuario.is_active:
                return Response({"error": "Cuenta desactivada. Contacte al administrador."}, status=status.HTTP_400_BAD_REQUEST)
            refresh = RefreshToken.for_user(usuario)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': usuario.id  
            })
        else:
            return Response({"error": "Credenciales inválidas."}, status=status.HTTP_400_BAD_REQUEST)

# Vista para obtener el perfil del usuario autenticado
class PerfilView(generics.RetrieveAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        usuario = request.user
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

# Vista para desactivar un usuario
# class DesactivarUsuarioView(generics.UpdateAPIView):
#     queryset = get_user_model().objects.all()
#     serializer_class = UsuarioSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def patch(self, request, *args, **kwargs):
#         usuario = self.get_object()
#         usuario.is_active = False
#         usuario.save()
#         return Response({"mensaje": "Usuario desactivado correctamente."}, status=status.HTTP_200_OK)

