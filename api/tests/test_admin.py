from api.celery import app
from django.contrib.auth.hashers import make_password
from api.admin import ImagesForm
import time
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import Images, UserProfile
from django.contrib.auth.models import User


class ImagesAdminTests(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            username="testuser",
            email="testuser@example.com",
            password="Haslo1234",
        )
        self.user_profile = UserProfile.objects.create(
            user=self.superuser, account_type=UserProfile.ENTERPRISE
        )
        self.image_data = BytesIO()
        self.image = Image.new("RGB", (900, 900))
        self.image.save(self.image_data, format="JPEG")
        self.image_data.seek(0)
        self.image_to_upload = SimpleUploadedFile(
            "test_image.jpg", self.image_data.getvalue(), content_type="image/jpeg"
        )
        self.data = {
            "title": "Test Image",
            "slug": "test-image",
            "image": self.image_to_upload,
            "author": self.superuser,
        }

        self.client.login(username="testuser", password="Haslo1234")

    def test_login(self):

        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.superuser.is_authenticated)
        self.assertTrue(self.superuser.is_staff)

    # def test_create_image(self):
    #     #data_extend = {"expiring_seconds":15}
    #     #response = self.client.post(reverse("admin:api_images_add"), data=dict(self.data, **data_extend), follow=True)
    #     response = self.client.post(reverse("admin:api_images_add"), data=self.data,format="multipart", follow=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(Images.objects.count(), 1)
    #     image = Images.objects.first()
    #     self.assertEqual(image.title, "Test Image")
    #     time.sleep(20)
    #     image.refresh_from_db()
    #     self.assertEqual(Images.objects.count(), 0)

    # def test_delete_image(self):
    #     # Test deleting an image
    #     image = Images.objects.create(title="Test Image", slug="test-image", image=self.image_to_upload, author=self.superuser)
    #     response = self.client.post(reverse("admin:api_image_delete", args=[image.id]))
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Images.objects.count(), 0)

    # def test_delete_object_image(self):
    #     obj = Images.objects.create(
    #         image=self.image_to_upload,
    #         author=self.superuser,
    #         expiration_time=600,
    #     )

    #     self.assertEqual(Images.objects.count(), 1)

    #     url = reverse("admin:api_images_delete", args=[obj.pk])
    #     response = self.client.post(url, data={"post": "yes"}, follow=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(Images.objects.count(), 0)

    # def test_create_image_with_expiration_seconds(self):
    #     obj = Images.objects.create(
    #         image=self.image_to_upload,
    #         author=self.superuser,
    #         expiring_seconds=1,
    #     )

    #     self.assertEqual(Images.objects.count(), 1)
    #     # time.sleep(31)
    #     obj.refresh_from_db()
    #     self.assertEqual(Images.objects.count(), 0)

    # def test_create_image_with_custom_thumbnails(self):
    #     d = {
    #         "title": "Test Image",
    #         "slug": "test-image",
    #         "image": self.image_to_upload,
    #         "author": self.superuser.id,
    #         # "thumbnail_width": 30,
    #         # "thumbnail_height": 30,
    #         # "created": datetime.date.today(),
    #     }
    #     url = reverse("admin:api_images_add")
    #     # form = ImagesForm(data=d, files=d)
    #     # self.assertTrue(form.is_valid())
    #     #response = self.client.post(url, data=d, follow=True, format="multipart")
    #     #url = reverse("admin:api_images_delete", args=[obj.pk])
    #     response = self.client.post(url, data=d)
    #     #print(response.context)
    #     print(Images.objects.all())
    #     #self.assertEqual(response.status_code, 302)
    #     self.assertEqual(Images.objects.count(), 1)
    #     image = Images.objects.first()
    #     self.assertEqual(image.author, self.superuser)
    #     self.assertEqual(image.thumbnail.thumbnail_custom.width, 30)
    #     self.assertEqual(image.thumbnail.thumbnail_custom.height, 30)

    # def test_create_image_without_superuser(self):
    #     """
    #     Test creating an image without logging in as a superuser
    #     """
    #     self.client.logout()
    #     url = reverse("admin:api_images_add")

    #     response = self.client.post(url, self.data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, f"{reverse('admin:login')}?next={url}")

    # def test_create_image_with_thumbnail_and_expiration(self):
    #     """
    #     Test that an image can be created with a custom thumbnail and an expiration time
    #     """

    #     # create image with a thumbnail
    #     data_extend = {
    #         "thumbnail_width": 200,
    #         "thumbnail_height": 200,
    #         "expiring_seconds": 45,  # 1 hour
    #     }
    #     response = self.client.post(
    #         reverse("admin:api_images_add"), data=dict(self.data, **data_extend)
    #     )
    #     print(response)
    #     image = Images.objects.first()
    #     image.refresh_from_db()
    #     self.assertEqual(
    #         response.status_code, 302
    #     )  # should be a redirect to the changelist
    #     self.assertEqual(Images.objects.count(), 1)

    #     self.assertIsNotNone(image.thumbnail)  # thumbnail should be generated
    #     self.assertIsNotNone(image.expiration_time)  # expiration_time should be set

    def tearDown(self):
        time.sleep(1.5)
        for image in Images.objects.all():
            image.delete()
