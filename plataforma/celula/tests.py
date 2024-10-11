from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from modulo.models import Modulo
from proyecto.models import Proyecto
from participante.models import Participante
from .models import Celula, Edicion

# Obtener el modelo de usuario personalizado
User = get_user_model()

# Clase de pruebas para la API de Celula
class CelulaAPITests(APITestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',  # Nombre de usuario
            password='testpass123',  # Contraseña
            email='test@example.com'  # Correo electrónico
        )
        
        # Crear un participante asociado al usuario de prueba
        self.participante = Participante.objects.create(
            usuario=self.user,  # Usuario asociado
            rol='Estudiante',  # Rol del participante
            descripcion='Participante de prueba'  # Descripción del participante
        )

        # Crear un módulo de prueba
        self.modulo = Modulo.objects.create(nombre="Modulo Test")
        # Crear un proyecto de prueba asociado al módulo
        self.proyecto = Proyecto.objects.create(nombre="Proyecto Test", modulo=self.modulo)
        # Crear una edición de prueba asociada al proyecto
        self.edicion = Edicion.objects.create(nombre="Edicion Test", proyecto=self.proyecto)
        # Crear una célula de prueba asociada a la edición
        self.celula = Celula.objects.create(nombre="Celula Test", descripcion="Descripción Test", edicion=self.edicion)
        # Añadir el participante a la célula
        self.celula.participantes.add(self.participante)

    # Prueba para crear una célula
    def test_crear_celula(self):
        # URL para crear una célula
        url = reverse('celula-list')
        # Datos para crear una nueva célula
        data = {
            "nombre": "Célula de Ejemplo",  # Nombre de la célula
            "descripcion": "Descripción de la célula de ejemplo",  # Descripción de la célula
            "edicion": self.edicion.id,  # ID de la edición asociada
            "participantes": [self.participante.id]  # Lista de IDs de participantes
        }
        # Enviar una solicitud POST para crear la célula
        response = self.client.post(url, data, format='json')
        # Imprimir el contenido de la respuesta (opcional para depuración)
        print(response.content)
        # Verificar que la respuesta sea de estado HTTP 201 (creado)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Prueba para obtener una célula
    def test_get_celula(self):
        # URL para obtener los detalles de una célula específica
        url = reverse('celula-detail', args=[self.celula.id])
        # Enviar una solicitud GET para obtener los detalles de la célula
        response = self.client.get(url, format='json')
        # Verificar que la respuesta sea de estado HTTP 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
