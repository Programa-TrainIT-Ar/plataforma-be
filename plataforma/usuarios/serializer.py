# serializer.py
from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import  force_str

class UsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'es_administrador', 'fecha_nacimiento', 'is_active']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            usuario = Usuario.objects.get(email=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("No existe un usuario con ese correo electrónico.")
        return value

class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password_confirmation": "Las contraseñas no coinciden."})
        return data

    def save(self, user):
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user
