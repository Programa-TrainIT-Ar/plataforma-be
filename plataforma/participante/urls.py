from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipanteViewSet, buscar_participante_por_id,  EnviarInvitacionView, ActivarInvitacionView

router = DefaultRouter()
router.register(r'participantes', ParticipanteViewSet, basename='participante')

urlpatterns = [
    path('', include(router.urls)),
    path('buscar/<int:id>/', buscar_participante_por_id, name='buscar_participante_por_id'),
    path('invitacion/enviar/', EnviarInvitacionView.as_view(), name='enviar_invitacion'),
    path('invitacion/activar/<uuid:token>/', ActivarInvitacionView.as_view(), name='activar_invitacion'),
]
