# # Django-DRF-IMAGE-UPLOADER

# General info

Django DRF project based on creating thumbnail of uploaded images e.g. .png .jpg

User Profile with account type Enterprise are able to: upload images and get thumbnail 200x200 and 400x400 also they can set expiration time.

User Profile with account type Premium are able to: upload images and get thumbnail 200x200 and 400x400.

User Profile with account type Basic are able to: upload images and get thumbnail 200x200.

and

Admin/superusers are able to create arbitrary thumbnail sizes

# Project is available also on HEROKU

.herokuapp.com/ in progres

# Features

- 80% test coverage
  <picture>
  <img alt="" src="https://i.imgur.com/L2Kl4VO.png">
  </picture>

# Technologies

# Setup

1. Requirements
   check requirements.txt

2.  Install package with pip or pipenv

```
    $ pip install django_drf_image_uploader
```
or
```
    $ pipenv install Django-Blog-Medium
```

3. Create api app database tables

- python or python3 manage.py makemigrations api
- python or python3 manage.py migrate
- python or python3 manage.py createsuperuser
- python manage.py createsuperuser
- python manage.py changepassword e.g. admin

# Setup on Docker

1. docker build -t api_images .

2. docker run -p 8000:8000 api_images

3. docker exec -it 7165010a8c00 python manage.py createsuperuser
4. docker exec -it 7165010a8c00 python manage.py changepassword e.g. admin


# how to use:
1. http://127.0.0.1:8000/login
2. http://127.0.0.1:8000/create
3. http://127.0.0.1:8000/images

# Screenshots

<picture>
  <img alt="" src="https://i.imgur.com/LkdVDtm_d.webp?maxwidth=760&fidelity=grand">
</picture>
<picture>
  <img alt="" src="https://i.imgur.com/l3I5VUK.png">
</picture>
<picture>
  <img alt="" src="https://i.imgur.com/F4kXVTJ_d.webp?maxwidth=760&fidelity=grand">
</picture>
