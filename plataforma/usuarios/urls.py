# plataforma\usuarios\urls.py
from django.urls import path
from .views import RegistroView, ActivarView
from . import views

urlpatterns = [
    path("registro/", RegistroView.as_view(), name="register"),
    path("activar/<str:token>/", ActivarView.as_view(), name="activate"),
    path("iniciar-sesion/", views.IniciarSesionView.as_view(), name="iniciar-sesion"),
    path("auth0/login/", views.Auth0LoginView.as_view(), name="auth0_login"),
    path("auth0/callback/", views.Auth0CallbackView.as_view(), name="auth0_callback"),
    path("perfil/", views.PerfilView.as_view(), name="perfil"),
    # path('desactivar/<int:pk>/', views.DesactivarUsuarioView.as_view(), name='desactivar-usuario'),
]
