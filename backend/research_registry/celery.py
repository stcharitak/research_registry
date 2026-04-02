import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "research_registry.settings")

app = Celery("research_registry")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
