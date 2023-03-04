import os
from django.contrib.auth import logout
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .serializers import ImagesSerializer
from django.contrib.auth.views import LoginView
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.signing import Signer
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from .models import Images, UserProfile


class LoginView(LoginView):
    template_name = "login.html"
    success_url = reverse_lazy("api:create")


class LogoutView(RedirectView):
    url = reverse_lazy("api:login")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class ImagesCreateView(generics.CreateAPIView):
    queryset = Images.objects.all()
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        account_type = self.request.user.userprofile.account_type
        allowed_methods = ["POST", "OPTIONS"]
        info_message = "Your account is None type change it in admin panel"
        detail_message = 'Method "{}" not allowed. Please use one of the following methods: {}.'.format(
            request.method, ", ".join(allowed_methods)
        )
        if account_type == UserProfile.NONE:
            data = {
                "detail": detail_message,
                "info": info_message,
                "account_type": account_type,
            }
        else:
            data = {"detail": detail_message, "info": ""}  # Your account is allowet to
        return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserImagesListView(ListAPIView):
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Images.objects.filter(author=user)


class GenerateExpiringLink(APIView):
    def get(self, request, slug):
        image = get_object_or_404(Images, slug=slug)
        if image.expiration:
            raise Http404("This image has expired")
        remaining_time = image.get_expiration_time(image.expiration_time)
        if remaining_time is None:
            raise Http404("This image has no expiration time")
        signer = Signer()
        signed_value = signer.sign(image.slug)
        url = request.build_absolute_uri(f"{settings.BASE_URL}/images/{signed_value}")
        response_data = {
            "url": url,
            "expiration_time": remaining_time,
        }
        return Response(response_data)


class OriginalFileLink(View):
    def get(self, request, id):
        try:
            image = Images.objects.get(id=id)
        except Images.DoesNotExist:
            raise Http404("Image does not exist")

        # Get the path to the original file
        file_path = os.path.join(settings.MEDIA_ROOT, str(image.image))

        # Check if the file exists
        if not default_storage.exists(file_path):
            raise Http404("Original file does not exist")

        # Get the URL for the original file and return it in the response
        file_url = default_storage.url(file_path)
        return HttpResponse(file_url)
