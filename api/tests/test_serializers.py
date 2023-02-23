import time
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from api.models import UserProfile, Images
from api.serializers import UserProfileSerializer, ImagesSerializer
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO
from api.celery import app


class UserProfileSerializerTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            email="testuser@test.com",
        )

        self.user_profile = UserProfile.objects.create(
            user=self.user, account_type=UserProfile.ENTERPRISE
        )

    def test_serialized_fields(self):
        request = self.factory.get("/")
        serialized_data = UserProfileSerializer(
            instance=self.user_profile, context={"request": request}
        ).data

        self.assertCountEqual(serialized_data.keys(), ["id", "user", "account_type"])
        self.assertEqual(serialized_data["id"], 1)
        self.assertEqual(serialized_data["account_type"], "Enterprise")


class ImagesSerializerTestCase(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            email="testuser@test.com",
        )

        self.user_profile = UserProfile.objects.create(
            user=self.user, account_type=UserProfile.ENTERPRISE
        )
        # Create an image file
        image_data = BytesIO()
        image = Image.new("RGB", (900, 900))
        image.save(image_data, format="JPEG")
        image_data.seek(0)
        self.image = SimpleUploadedFile(
            "test_image.jpg", image_data.getvalue(), content_type="image/jpeg"
        )
        self.data = {
            "title": "test_image",
            "slug": "test_image",
            "image": self.image,
            "author": self.user,
        }

    def test_create_image(self):
        request = self.factory.get("/")
        request.user = self.user

        serializer = ImagesSerializer(data=self.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        image = serializer.save()
        image.refresh_from_db()

        self.assertEqual(Images.objects.count(), 1)
        self.assertEqual(image.author, self.user)
        self.assertIsNotNone(image.slug)
        self.assertIsNotNone(image.created)
        self.assertIsNone(image.expiration_time)
        self.assertIsNotNone(image.thumbnail)

    def test_get_thumbnail_200(self):
        request = self.factory.get("/")
        request.user = self.user

        image = Images.objects.create(
            title="test_image",
            slug="test_image",
            image=self.image,
            author=self.user,
        )

        image.refresh_from_db()
        serializer = ImagesSerializer(instance=image, context={"request": request})

        self.assertEqual(
            serializer.data["thumbnail_200"],
            f"http://testserver/media/{image.thumbnail.thumbnail_200}",
        )

    def test_get_thumbnail_400(self):
        request = self.factory.get("/")
        request.user = self.user
        image = Images.objects.create(
            title="test_image",
            image=self.image,
            author=self.user,
        )

        image.refresh_from_db()
        serializer = ImagesSerializer(instance=image, context={"request": request})

        self.assertEqual(
            serializer.data["thumbnail_400"],
            f"http://testserver/media/{image.thumbnail.thumbnail_400}",
        )

#This test takes over 5 minutes, keep it comment
    # def test_remaining_time(self):
    #     request = self.factory.get("/")
    #     request.user = self.user
    #     image = Images.objects.create(
    #         title="Test Image", image=self.image, author=self.user, expiration_time=300
    #     )
    #     serializer = ImagesSerializer(instance=image, context={"request": request})

    #     expected_data = "http://127.0.0.1:8000/media/expired.png"

    #     time.sleep(301)
    #     image.refresh_from_db()

    #     self.assertEqual(serializer.data["image"], expected_data)
