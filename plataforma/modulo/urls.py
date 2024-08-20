from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModuloViewSet

router = DefaultRouter()
router.register(r'modulos', ModuloViewSet, basename='modulo')

urlpatterns = [
    path('', include(router.urls)),
]
