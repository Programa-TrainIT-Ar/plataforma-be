from rest_framework import viewsets
from .models import Modulo
from .serializers import ModuloSerializer

class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer
