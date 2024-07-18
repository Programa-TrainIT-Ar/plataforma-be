from rest_framework import viewsets, status
from .models import Participante
from .serializers import ParticipanteSerializer, InvitacionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.utils import timezone
from usuarios.models import Usuario
from django.conf import settings
import datetime


class ParticipanteViewSet(viewsets.ModelViewSet):
    queryset = Participante.objects.all()
    serializer_class = ParticipanteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()


@api_view(["GET"])
def buscar_participante_por_id(request, id):
    try:
        participante = Participante.objects.get(id=id)
        serializer = ParticipanteSerializer(participante)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Participante.DoesNotExist:
        return Response(
            {"error": "Participante no encontrado"}, status=status.HTTP_404_NOT_FOUND
        )


class EnviarInvitacionView(APIView):
    def post(self, request):
        serializer = InvitacionSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            # Otras validaciones y lógica
            usuario = Usuario.objects.filter(email=email).first()
            if not usuario:
                return Response(
                    {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )

            # Crear o actualizar participante
            participante, created = Participante.objects.get_or_create(usuario=usuario)
            participante.token_expires = timezone.now() + datetime.timedelta(days=1)
            participante.save()

            # Enviar email de invitación
            send_mail(
                "Invitación a participar",
                f"Utiliza este token para aceptar la invitación: {participante.invitacion_tokens}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response(
                {"message": "Invitación enviada con éxito"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivarInvitacionView(APIView):
    def post(self, request, token):
        try:
            participante = Participante.objects.get(invitacion_tokens=token)
            if participante.token_expires < timezone.now():
                return Response(
                    {"error": "El token ha expirado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            participante.invitacion_aceptada = True
            participante.invitacion_tokens = None  
            participante.token_expires = None
            participante.save()
            return Response(
                {"message": "Invitación aceptada con éxito"}, status=status.HTTP_200_OK
            )
        except Participante.DoesNotExist:
            return Response(
                {"error": "Token inválido"}, status=status.HTTP_404_NOT_FOUND
            )