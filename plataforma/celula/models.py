from django.db import models
from edicion.models import Edicion  
from participante.models import Participante  

class Celula(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    edicion = models.ForeignKey(Edicion, related_name="celulas", on_delete=models.CASCADE)
    participantes = models.ManyToManyField(Participante, related_name="celulas")
