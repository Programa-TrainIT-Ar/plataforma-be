from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from modulo.models import Modulo
from .models import Proyecto

# Obtener el modelo de usuario
User = get_user_model()

class ProyectoAPITests(APITestCase):
    def setUp(self):
        # Crear un usuario de prueba y autenticar al cliente con ese usuario
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        # Crear un módulo de prueba
        self.modulo = Modulo.objects.create(nombre="Modulo Test")

    def test_crear_proyecto(self):
        # Obtener la URL para la vista de lista de proyectos
        url = reverse('proyecto-list')
        
        # Datos para crear un nuevo proyecto
        data = {
            "nombre": "Proyecto Test",
            "descripcion": "Descripción del proyecto",
            "modulo": self.modulo.id
        }
        
        # Realizar una solicitud POST para crear un nuevo proyecto
        response = self.client.post(url, data, format='json')
        
        # Verificar que la respuesta tenga el estado HTTP 201 (creado)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_proyecto(self):
        # Crear un proyecto de prueba
        proyecto = Proyecto.objects.create(nombre="Proyecto Test", modulo=self.modulo)
        
        # Obtener la URL para la vista de detalle del proyecto
        url = reverse('proyecto-detail', args=[proyecto.id])
        
        # Realizar una solicitud GET para obtener los detalles del proyecto
        response = self.client.get(url)
        
        # Verificar que la respuesta tenga el estado HTTP 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
