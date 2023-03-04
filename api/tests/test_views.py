import os
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from api.models import Images, UserProfile
from PIL import Image
from io import BytesIO
from django.urls import reverse
from api.celery import app
import time

User = get_user_model()


class LoginViewTestCase(APITestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "test"
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_valid_login(self):
        url = reverse_lazy("api:login")
        data = {"username": self.username, "password": self.password}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_authenticated)


    def test_invalid_login(self):
        url = reverse_lazy("api:login")
        data = {"username": self.username, "password": "wrongpass"}
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_authenticated)



class ImagesCreateViewTestCase(APITestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="testuser", email="testuser@test.com", password="testpass"
        )

        image_data = BytesIO()
        image = Image.new("RGB", (900, 900))
        image.save(image_data, format="JPEG")
        image_data.seek(0)
        self.image = SimpleUploadedFile(
            "test_image.jpg", image_data.getvalue(), content_type="image/jpeg"
        )

        self.data = {
            "title": "Test Image",
            "slug": "test-image",
            "image": self.image,
        }

    def test_create_image_valid_data(self):

        self.user_profile = UserProfile.objects.create(
            user=self.user, account_type=UserProfile.ENTERPRISE
        )
        self.client.force_authenticate(user=self.user)

        data_extend = {
            "author": self.user.pk,
            "expiration_time": 600,
        }

        url = reverse("api:create")
        response = self.client.post(
            url,
            data=dict(self.data, **data_extend),
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Images.objects.count(), 1)

    def test_create_image_invalid_data(self):
        self.user_profile = UserProfile.objects.create(
            user=self.user, account_type=UserProfile.ENTERPRISE
        )
        self.client.force_authenticate(user=self.user)
        data_extend = {"author": self.user.pk, "expiration_time": 200}

        url = reverse("api:create")
        response = self.client.post(
            url,
            data=dict(self.data, **data_extend),
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Images.objects.count(), 0)

    def test_create_image_user_basic(self):

        UserProfile.objects.create(user=self.user, account_type=UserProfile.BASIC)
        self.client.force_authenticate(user=self.user)

        data_extend = {
            "author": self.user.pk,
            "expiration_time": 400,
        }

        url = reverse("api:create")
        response = self.client.post(
            url,
            data=dict(self.data, **data_extend),
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Images.objects.count(), 1)

        for images in Images.objects.all():
            self.assertTrue(images.thumbnail.thumbnail_200)
            self.assertFalse(images.thumbnail.thumbnail_400)
            self.assertFalse(images.expiration_time)

    def tearDown(self):
        time.sleep(1.5)
        for image in Images.objects.all():
            image.delete()