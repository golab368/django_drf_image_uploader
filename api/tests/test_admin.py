# from django.contrib.auth import get_user_model
# from django.test import TestCase, Client
# from django.urls import reverse
# from django.core.files.uploadedfile import SimpleUploadedFile
# from PIL import Image
# from io import BytesIO
# from datetime import timedelta
# from unittest import mock

# from api.models import Images, UserProfile
# from api.admin import ImagesAdmin, ImagesForm


# class ImagesAdminTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.admin_user = get_user_model().objects.create_superuser(
#             username='admin', password='adminpassword', email='admin@test.com'
#         )
#         self.user_profile = UserProfile.objects.create(
#             user=self.admin_user, account_type=UserProfile.ENTERPRISE
#         )
#         self.client.force_login(self.admin_user)

#     @mock.patch('django.utils.timezone.now')
#     def test_create_image_with_expiration_time(self, mock_now):


#         image_data = BytesIO()
#         Image.new('RGBA', size=(100, 100), color=(155, 0, 0)).save(image_data, 'png')
#         image_data.seek(0)
#         image_file = SimpleUploadedFile('test_image.png', image_data.read(), content_type='image/png')

#         add_image_url = '/admin/images/add/'
#         response = self.client.get(add_image_url)

#         self.assertEqual(response.status_code, 200)
#        # self.assertIsInstance(response.context['adminform'].form, ImagesForm)

#         post_data = {
#             'title': 'Test Image',
#             'image': image_file,
#             'original_file_link': image_file.name,
#             'expiring_seconds': 30,
#         }
#         response = self.client.post(add_image_url, post_data, follow=True)

#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'added successfully')

#         created_image = Images.objects.get(title='Test Image')
#         expiration_time = created_image.expiration_time
#         self.assertIsNotNone(expiration_time)

#         generate_expiring_link_url = reverse('admin:api_images_images_generate_expiring_link', args=[created_image.pk])
#         response = self.client.get(generate_expiring_link_url)

#         self.assertEqual(response.status_code, 200)
#         response_data = response.json()
#         self.assertEqual(response_data['url'], created_image.get_expiring_link())
#         self.assertAlmostEqual(response_data['expiration_time'], expiration_time.total_seconds(), delta=1)
