from rest_framework import serializers
from usuarios.models import Usuario
from .models import Participante


class ParticipanteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Participante
        fields = [
            "id",
            "usuario",
            "rol",
            "descripcion",
            "invitacion_aceptada",
            "invitacion_tokens",
        ]
        read_only_fields = ["id", "invitacion_aceptada", "invitacion_tokens"]

    def create(self, validated_data):
        usuario_data = validated_data.pop("usuario")
        usuario_id = usuario_data.id

        # Verificar si ya existe un participante asociado a este usuario
        existing_participante = Participante.objects.filter(
            usuario_id=usuario_id
        ).first()
        if existing_participante:
            # Puedo manejar el caso de error o actualizar el participante existente aquí
            # Ejemplo: existing_participante.rol = validated_data['rol']
            # existing_participante.descripcion = validated_data['descripcion']
            # existing_participante.save()
            raise serializers.ValidationError(
                "Este usuario ya está asociado a un participante existente."
            )

        # Crear el participante asociado al usuario
        participante = Participante.objects.create(
            usuario_id=usuario_id, **validated_data
        )
        return participante


class InvitacionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    modulo_id = serializers.IntegerField(required=False)
    proyecto_id = serializers.IntegerField(required=False)
    edicion_id = serializers.IntegerField(required=False)
    celula_id = serializers.IntegerField(required=False)
