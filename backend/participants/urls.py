from rest_framework.routers import DefaultRouter

from .views import ParticipantViewSet

router = DefaultRouter()
router.register("participants", ParticipantViewSet, basename="participant")

urlpatterns = router.urls
