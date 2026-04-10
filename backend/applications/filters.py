import django_filters

from .models import Application


class ApplicationFilter(django_filters.FilterSet):
    class Meta:
        model = Application
        fields = {
            "status": ["exact"],
            "study": ["exact"],
            "participant": ["exact"],
            "reviewed_by": ["exact"],
        }
