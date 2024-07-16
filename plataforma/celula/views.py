from rest_framework import viewsets
from .models import Celula
from .serializers import CelulaSerializer
from rest_framework.response import Response
from rest_framework import status

class CelulaViewSet(viewsets.ModelViewSet):
    queryset = Celula.objects.all()
    serializer_class = CelulaSerializer

    def create(self, request):
        serializer = CelulaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)