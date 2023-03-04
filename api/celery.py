# import os
# from celery import Celery

# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_images.settings")


# app = Celery("api")
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks(["api.tasks"])
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_images.settings")

app = Celery("api", broker=os.environ['REDIS_URL'])
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

app.autodiscover_tasks(['api.tasks'])

