import os
from celery import Celery
from django.conf import settings
# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_images.settings")
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')


app = Celery("api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])
# app.autodiscover_tasks(["api.tasks"])
from api.tasks import generate_thumbnail
app.autodiscover_tasks(lambda: [generate_thumbnail])

