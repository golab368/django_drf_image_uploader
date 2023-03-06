from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_images.settings")

app = Celery("api")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(BROKER_URL=os.environ.get('REDIS_URL'),
                CELERY_RESULT_BACKEND=os.environ.get('REDIS_URL'))

app.autodiscover_tasks(['api'], force=True)

