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

app = Celery("api")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Update broker URL to use Redis
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])
# redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
# app.conf.update(BROKER_URL=redis_url)
# print(f'BROKER_URL set to {redis_url}')

# Automatically discover tasks in the 'api.tasks' module
app.autodiscover_tasks(['api.tasks'])

