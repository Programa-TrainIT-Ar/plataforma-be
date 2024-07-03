from django.db import models

class Modulo(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
