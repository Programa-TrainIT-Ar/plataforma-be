# plataforma/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/usuarios/", include("usuarios.urls")),
    path("api/participante/", include("participante.urls")),
    path("api/proyecto/", include("proyecto.urls")),
    path("api/edicion/", include("edicion.urls")),
    path("api/celula/", include("celula.urls")),
    path("api/modulo/", include("modulo.urls")),
]
