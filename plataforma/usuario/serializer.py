from rest_framework import serializers
from .models import Users
from django.contrib.auth.hashers import make_password


class UsersSerializer(serializers.ModelSerializer):
    #solo escritura y obligatorio
    password = serializers.CharField(write_only=True , required=True)


    class Meta:
        model = Users
        fields = ['username', 'email', 'password', 'is_admin', 'date_birth','is_active']

    def create(self, validated_data):
        #encripta la contraseña
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)