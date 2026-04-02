from rest_framework.routers import DefaultRouter

from .views import ExportJobViewSet

router = DefaultRouter()
router.register("exports", ExportJobViewSet, basename="export-job")

urlpatterns = router.urls
