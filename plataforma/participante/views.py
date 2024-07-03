from rest_framework import viewsets
from .models import Participante
from .serializers import (
    ParticipanteSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


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
    pass


class ActivarInvitacionView(APIView):
    pass
