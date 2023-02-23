from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO
from api.models import Images, UserProfile
from api.celery import app
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = "testuser"
    password = "testpass"
    email = "test@example.com"


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    account_type = UserProfile.ENTERPRISE


class ImagesModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        image_data = BytesIO()
        image = Image.new("RGB", (900, 900))
        image.save(image_data, format="JPEG")
        image_data.seek(0)
        cls.image = SimpleUploadedFile(
            "test_image.jpg", image_data.getvalue(), content_type="image/jpeg"
        )

    def test_create_image_user_enterprise_with_expiration_time(self):

        user = UserFactory()
        UserProfileFactory(user=user, account_type=UserProfile.ENTERPRISE)

        image_obj = Images.objects.create(
            image=self.image,
            author=user,
            expiration_time=600,
        )

        image_obj.refresh_from_db()
        self.assertEqual(
            image_obj.author.userprofile.account_type, UserProfile.ENTERPRISE
        )
        self.assertEqual(image_obj.expiration_time, 600)
        self.assertTrue(image_obj.thumbnail is not None)
        self.assertTrue(image_obj.thumbnail.thumbnail_200.name)
        self.assertTrue(image_obj.thumbnail.thumbnail_400.name)
        self.assertTrue(image_obj.thumbnail.thumbnail_200)

        self.assertIsNotNone(image_obj.thumbnail.thumbnail_200)

    def test_create_image_for_user_premium(self):
        user = UserFactory()
        UserProfileFactory(user=user, account_type=UserProfile.PREMIUM)

        image_obj = Images.objects.create(
            image=self.image,
            author=user,
            expiration_time=600,
        )

        image_obj.refresh_from_db()
        self.assertEqual(image_obj.author.userprofile.account_type, UserProfile.PREMIUM)
        self.assertTrue(image_obj.thumbnail is not None)
        self.assertTrue(image_obj.thumbnail.thumbnail_200.name)
        self.assertTrue(image_obj.thumbnail.thumbnail_400.name)

    def test_create_image_for_user_basic(self):
        user = UserFactory()
        UserProfileFactory(user=user, account_type=UserProfile.BASIC)

        image_obj = Images.objects.create(
            image=self.image,
            author=user,
        )

        image_obj.refresh_from_db()
        self.assertEqual(image_obj.author.userprofile.account_type, UserProfile.BASIC)
        self.assertEqual(image_obj.expiration_time, None)
        self.assertTrue(image_obj.thumbnail is not None)
        self.assertTrue(image_obj.thumbnail.thumbnail_200.name)
        self.assertFalse(image_obj.thumbnail.thumbnail_400.name)
