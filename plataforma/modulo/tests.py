# modulo/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Modulo

User = get_user_model()

class ModuloAPITests(APITestCase):
    def setUp(self):
        # Crear un usuario de prueba y autenticarlo
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)

    def test_crear_modulo(self):
        # URL para la creación de módulos
        url = reverse('modulo-list')
        data = {
            "nombre": "Modulo Test",
            "descripcion": "Descripción del módulo"
        }
        # Realizar una solicitud POST para crear un módulo
        response = self.client.post(url, data, format='json')
        # Verificar que la respuesta sea 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_modulo(self):
        # Crear un módulo de prueba
        modulo = Modulo.objects.create(nombre="Modulo Test")
        # URL para obtener los detalles de un módulo
        url = reverse('modulo-detail', args=[modulo.id])
        # Realizar una solicitud GET para obtener el módulo
        response = self.client.get(url)
        # Verificar que la respuesta sea 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
