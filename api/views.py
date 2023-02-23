from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm


from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView
from rest_framework import generics

from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .models import Images
from rest_framework import status
from .serializers import ImagesSerializer


class LoginView(FormView):
    template_name = "login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy("api:create")

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        return super().form_valid(form)


class LogoutView(RedirectView):
    success_url = reverse_lazy("api:login")

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


class UserImagesListView(ListAPIView):
    serializer_class = ImagesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Images.objects.filter(author=user)
