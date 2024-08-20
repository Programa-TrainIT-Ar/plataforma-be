# usuarios/tests.py

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

# Obtener el modelo de usuario
User = get_user_model()

class UsuarioAPITests(APITestCase):
    def test_registro_usuario(self):
        # Obtener la URL para la vista de registro de usuario
        url = reverse('register')
        
        # Datos para registrar un nuevo usuario
        data = {
            "username": "newuser",  # Nombre de usuario
            "email": "newuser@example.com",  # Correo electrónico del usuario
            "password": "newpass123",  # Contraseña del usuario
            "es_administrador": False,  # Indica si el usuario es un administrador
            "fecha_nacimiento": "1990-01-01",  # Fecha de nacimiento del usuario
            "is_active": False  # Estado de activación del usuario
        }
        
        # Realizar una solicitud POST para registrar un nuevo usuario
        response = self.client.post(url, data, format='json')
        
        # Verificar que la respuesta tenga el estado HTTP 201 (creado)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_iniciar_sesion(self):
        # Crear un usuario de prueba
        User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        
        # Obtener la URL para la vista de inicio de sesión
        url = reverse('iniciar-sesion')
        
        # Datos para iniciar sesión
        data = {
            "email": "test@example.com",  # Correo electrónico del usuario
            "password": "testpass123"  # Contraseña del usuario
        }
        
        # Realizar una solicitud POST para iniciar sesión
        response = self.client.post(url, data, format='json')
        
        # Verificar que la respuesta tenga el estado HTTP 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la respuesta contenga un token de acceso
        self.assertIn('access', response.data)

    def test_perfil_usuario(self):
        # Crear un usuario de prueba
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        
        # Autenticar al cliente con el usuario creado
        self.client.force_authenticate(user=user)
        
        # Obtener la URL para la vista del perfil del usuario
        url = reverse('perfil')
        
        # Realizar una solicitud GET para obtener el perfil del usuario
        response = self.client.get(url)
        
        # Verificar que la respuesta tenga el estado HTTP 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
