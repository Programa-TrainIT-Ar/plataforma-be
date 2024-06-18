from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.hashers import make_password

# Definición del serializador para el modelo Usuario
class UsuarioSerializer(serializers.ModelSerializer):
    # Campo para manejar la contraseña de forma segura (solo escritura, obligatorio)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario  # Especifica el modelo que se va a serializar
        fields = ('username', 'email', 'password', 'fecha_nacimiento', 'es_administrador', 'is_active')

    def create(self, validated_data):
        # Sobrescribe el método create para asegurar la encriptación de la contraseña
        validated_data['password'] = make_password(validated_data.get('password'))  # Encripta la contraseña
        return super().create(validated_data)  # Llama al método create original del serializador
