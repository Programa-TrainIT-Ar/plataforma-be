from django.conf import settings
from django.db import models
import uuid


class Participante(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol = models.CharField(max_length=255)
    descripcion = models.TextField()
    invitacion_aceptada = models.BooleanField(default=False)
    invitacion_tokens = models.UUIDField(null=True, blank=True)
    token_expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"
