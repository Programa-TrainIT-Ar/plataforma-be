from rest_framework import serializers
from .models import Celula

class CelulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Celula
        fields = ["id", "nombre", "descripcion", "edicion", "participantes"]
