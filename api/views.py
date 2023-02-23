import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import default_storage
from django.core.signing import Signer
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .models import Images, UserProfile, Thumbnail
from rest_framework import status
from .serializers import ImagesSerializer

#from .tasks import generate_thumbnail

class LoginView(FormView):
    template_name = "login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy('api:create')

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        return super().form_valid(form)


class LogoutView(RedirectView):
    success_url = reverse_lazy('api:login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class ImagesCreateView(generics.CreateAPIView):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    # def get_serializer_class(self):
    #     #user = self.request.user
    #     # if user.userprofile.account_type in [UserProfile.BASIC, UserProfile.PREMIUM]:
    #     #     return ImagesSerializerWithoutExpiration
    #     return ImagesSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserImagesListView(ListAPIView):
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Images.objects.filter(author=user)


# from django.core.cache import cache
# from rest_framework.response import Response

# class ImagesCreateView(generics.CreateAPIView):
#     queryset = Images.objects.all()
#     permission_classes = [IsAuthenticated]
#     parser_classes = (MultiPartParser, FormParser, JSONParser)

#     def get_serializer_class(self):
#         user = self.request.user
#         if user.userprofile.account_type in [UserProfile.BASIC, UserProfile.PREMIUM]:
#             return ImagesSerializerWithoutExpiration
#         return ImagesSerializer

#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
#         image_path = serializer.validated_data['image'].path
#         process_image.delay(image_path)

#     def post(self, request, *args, **kwargs):
#         cache.delete(request.user.id)
#         return super().post(request, *args, **kwargs)

# class CustomPagination(PageNumberPagination):
#     page_size = 10

# class UserImagesListView(ListAPIView):
#     serializer_class = ImagesSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination

#     def get_queryset(self):
#         user = self.request.user
#         cache_key = user.id
#         images = cache.get(cache_key)
#         if not images:
#             images = Images.objects.filter(author=user)
#             for image in images:
#                 image_path = image.image.path
#                 process_image.delay(image_path)
#             cache.set(cache_key, images, timeout=60 * 5) # cache for 5 minutes
#         return images
