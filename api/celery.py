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

# Use Redis as the broker for Celery.
app = Celery("api", broker=os.environ["REDIS_URL"])

# Configure Celery using Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.
app.autodiscover_tasks(["api.tasks"])
