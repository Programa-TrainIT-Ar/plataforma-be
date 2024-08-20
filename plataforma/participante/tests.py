# participante/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Participante

User = get_user_model()

class ParticipanteAPITests(APITestCase):
    def setUp(self):
        # Crear un usuario de prueba y autenticarlo
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)

    def test_crear_participante(self):
        # URL para la creación de participantes
        url = reverse('participante-list')
        data = {
            "usuario": self.user.id,
            "rol": "Estudiante",
            "descripcion": "Participante de prueba"
        }
        # Realizar una solicitud POST para crear un participante
        response = self.client.post(url, data, format='json')
        # Verificar que la respuesta sea 201 CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_participante(self):
        # Crear un participante de prueba
        participante = Participante.objects.create(usuario=self.user, rol="Estudiante", descripcion="Test")
        # URL para obtener los detalles de un participante
        url = reverse('participante-detail', args=[participante.id])
        # Realizar una solicitud GET para obtener el participante
        response = self.client.get(url)
        # Verificar que la respuesta sea 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
