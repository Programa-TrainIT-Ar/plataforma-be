from django.db import models
from modulo.models import Modulo

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    modulo = models.ForeignKey(Modulo, related_name="proyectos", on_delete=models.CASCADE)
