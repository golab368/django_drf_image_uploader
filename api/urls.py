from django.urls import path
from .views import (
    ImagesCreateView,
    LoginView,
    LogoutView,
    UserImagesListView,
)

app_name = "api"

urlpatterns = [
    # other URL patterns here
    path("login/", LoginView.as_view(template_name='login.html'), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create/", ImagesCreateView.as_view(), name="create"),
    path(
        "images/",
        UserImagesListView.as_view(),
        name="user_images_list",
    ),

]
