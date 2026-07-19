import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Komail_Django.settings")

app = Celery("Komail_Django")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
