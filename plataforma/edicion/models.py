from django.db import models
from proyecto.models import Proyecto  

class Edicion(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    proyecto = models.ForeignKey(Proyecto, related_name="ediciones", on_delete=models.CASCADE)
