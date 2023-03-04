web: gunicorn api_images.wsgi --log-file -
release: python manage.py makemigrations api --noinput
release: python manage.py collectstatic --noinput
release: python manage.py migrate api --noinput
worker: celery --app apiimages worker -l info