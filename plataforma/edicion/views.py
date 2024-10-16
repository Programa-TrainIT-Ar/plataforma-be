from rest_framework import viewsets
from .models import Edicion
from .serializers import EdicionSerializer
from rest_framework.response import Response
from rest_framework import status

class EdicionViewSet(viewsets.ModelViewSet):
    queryset = Edicion.objects.all()
    serializer_class = EdicionSerializer

    def create(self, request):
        serializer = EdicionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)