from django.contrib.auth.models import AbstractUser
from django.db import models

# Definición del modelo de usuario personalizado que hereda de AbstractUser
class Usuario(AbstractUser):
    fecha_nacimiento = models.DateField(null=True, blank=True)
    es_administrador = models.BooleanField(default=False)

    # Método para representar el objeto como una cadena de texto
    def __str__(self):
        return self.username  # Devuelve el nombre de usuario como representación del objeto
