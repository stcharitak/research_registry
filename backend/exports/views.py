import os

from django.http import FileResponse, Http404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ExportJob, ExportJobStatus
from .serializers import ExportJobCreateSerializer, ExportJobReadSerializer
from .tasks import run_export_job


class ExportJobViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExportJob.objects.filter(requested_by=self.request.user).order_by(
            "-created_at"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ExportJobCreateSerializer
        return ExportJobReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = ExportJob.objects.create(
            requested_by=request.user,
            export_type=serializer.validated_data["export_type"],
            filters=serializer.validated_data.get("filters", {}),
        )

        run_export_job.delay(job.id)

        read_serializer = ExportJobReadSerializer(job, context={"request": request})
        return Response(read_serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        job = self.get_object()

        if job.status != ExportJobStatus.COMPLETED or not job.file:
            raise Http404("Export file is not available.")

        response = FileResponse(job.file.open("rb"), content_type="text/csv")
        filename = os.path.basename(job.file.name)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
