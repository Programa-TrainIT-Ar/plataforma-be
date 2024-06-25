from django.urls import path
from .views import RegisterView, ActivationView, LoginView, Auth0LoginView, Auth0CallbackView, PerfilView

urlpatterns = [
    path("registro/", RegisterView.as_view(), name="register"),
    path("activar/<str:token>/", ActivationView.as_view(), name="activate"),
    path("iniciar-sesion/", LoginView.as_view(), name="iniciar-sesion"),
    path("auth0/login/", Auth0LoginView.as_view(), name="auth0_login"),
    path("auth0/callback/", Auth0CallbackView.as_view(), name="auth0_callback"),
    path("perfil/", PerfilView.as_view(), name="perfil"),
]
