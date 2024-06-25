from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.hashers import make_password

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'es_administrador', 'fecha_nacimiento', 'is_active']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)
