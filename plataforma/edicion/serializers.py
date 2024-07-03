from rest_framework import serializers
from .models import Edicion

class EdicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Edicion
        fields = ["id", "nombre", "descripcion", "proyecto"]
