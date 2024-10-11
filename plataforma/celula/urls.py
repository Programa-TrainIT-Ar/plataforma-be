from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CelulaViewSet

router = DefaultRouter()
router.register(r'celulas', CelulaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
