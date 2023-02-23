from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    ImagesCreateView,
    # generate_expiring_link,
    # original_file_link,
    LoginView,
    LogoutView,
    UserImagesListView,
)

app_name = "api"

urlpatterns = [
    # other URL patterns here
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create/", ImagesCreateView.as_view(), name="create"),
    path(
        "images/",
        UserImagesListView.as_view(),
        name="user_images_list",
    ),
    # path(
    #     "generate-expiring-link/<slug:slug>/",
    #     generate_expiring_link,
    #     name="generate_expiring_link",
    # ),
    # path("original_file_link/<int:id>/", original_file_link, name="original_file_link"),
]
