from django.urls import path
from .views import (
    ImagesCreateView,
    LoginView,
    LogoutView,
    UserImagesListView,
    GenerateExpiringLink,
    OriginalFileLink,
)

app_name = "api"

urlpatterns = [
    # other URL patterns here
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create/", ImagesCreateView.as_view(), name="create"),
    path(
        "images/",
        UserImagesListView.as_view(),
        name="user_images_list",
    ),
    path("images/<slug:slug>/", GenerateExpiringLink.as_view(), name="expiring_link"),
    path("images/<int:id>/original/", OriginalFileLink.as_view(), name="original_file"),
]
