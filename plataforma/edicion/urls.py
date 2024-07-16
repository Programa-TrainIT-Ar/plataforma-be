from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EdicionViewSet

router = DefaultRouter()
router.register(r'ediciones', EdicionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
