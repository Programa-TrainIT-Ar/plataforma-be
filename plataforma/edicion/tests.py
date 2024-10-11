# edicion/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from modulo.models import Modulo
from proyecto.models import Proyecto
from .models import Edicion

User = get_user_model()

class EdicionAPITests(APITestCase):
    def setUp(self):
        # Crear un usuario de prueba y autenticarlo
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        # Crear un módulo y proyecto de prueba
        self.modulo = Modulo.objects.create(nombre="Modulo Test")
        self.proyecto = Proyecto.objects.create(nombre="Proyecto Test", modulo=self.modulo)

    def test_crear_edicion(self):
        # URL para la creación de ediciones
        url = reverse('edicion-list')
        data = {
            "nombre": "Edicion Test",
            "descripcion": "Descripción de la edición",
            "proyecto": self.proyecto.id
        }
        # Realizar una solicitud POST para crear una edición
        response = self.client.post(url, data, format='json')
        # Verificar que la respuesta sea 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_edicion(self):
        # Crear una edición de prueba
        edicion = Edicion.objects.create(nombre="Edicion Test", proyecto=self.proyecto)
        # URL para obtener los detalles de una edición
        url = reverse('edicion-detail', args=[edicion.id])
        # Realizar una solicitud GET para obtener la edición
        response = self.client.get(url)
        # Verificar que la respuesta sea 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
