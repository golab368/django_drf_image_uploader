import os
import uuid
from io import BytesIO
from PIL import Image

from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from .tasks import generate_thumbnail


def user_directory_path(instance, filename):
    extension = filename.split(".")[-1]
    return "{}.{}".format(uuid.uuid4(), extension)


class User(AbstractUser):
    def save(self, *args, **kwargs):
        if not self.pk:
            self.set_password(self.password)

        super(User, self).save(*args, **kwargs)


class UserProfile(models.Model):
    BASIC = "Basic"
    PREMIUM = "Premium"
    ENTERPRISE = "Enterprise"
    ACCOUNT_TIERS = (
        (BASIC, "Basic"),
        (PREMIUM, "Premium"),
        (ENTERPRISE, "Enterprise"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=255, choices=ACCOUNT_TIERS)

    def __str__(self):
        return self.user.username


class ThumbnailCustom(models.Model):
    thumbnail_custom = models.ImageField(null=True, blank=True)


class Thumbnail(models.Model):
    thumbnail_200 = models.ImageField(null=True, blank=True)
    thumbnail_400 = models.ImageField(null=True, blank=True)


class Images(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to=user_directory_path)
    slug = models.SlugField(max_length=250, unique_for_date="created")
    created = models.DateTimeField(default=timezone.now)
    original_file_link = models.URLField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="author")
    expiration = models.BooleanField(default=False)
    thumbnail = models.OneToOneField(
        Thumbnail,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="thumbnail",
    )
    thumbnail_custom = models.OneToOneField(
        ThumbnailCustom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="image_custom",
    )
    expiration_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Expiration time in seconds (300-3000)",
        validators=[MinValueValidator(300), MaxValueValidator(3000)],
    )
    # Additional field available for Admin or superusers
    expiring_seconds = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Enter a positive integer to set up expiration time",
    )

    def save(self, *args, **kwargs):
        filename = os.path.basename(self.image.name)
        title, _ = os.path.splitext(filename)
        self.title = title

        self.slug = slugify(self.title)

        user_profile = UserProfile.objects.get(user=self.author)

        account_tier = user_profile.account_type
        if self.image:
            self.original_file_link = self.image

        if not self.thumbnail:
            super().save(*args, **kwargs)
            generate_thumbnail.delay(self.image.name, account_tier)
        else:
            super().save(*args, **kwargs)

    def make_thumbnail_custom(self, thumbnail_custom, width, height):

        if width and height:
            size = (width, height)

        if self.image:
            image = Image.open(self.image)

            thumb_name = uuid.uuid4().hex
            thumb_extension = os.path.splitext(self.image.name)[1]
            thumb_filename = f"{thumb_name}_thumb_custom{size}{thumb_extension}"

            if thumb_extension in [".jpg", ".jpeg"]:
                FTYPE = "JPEG"
            elif thumb_extension == ".gif":
                FTYPE = "GIF"
            elif thumb_extension == ".png":
                FTYPE = "PNG"
            else:
                return False

            temp_thumb = BytesIO()
            image_copy = image.copy()
            image_copy.thumbnail(size)
            image_copy.save(temp_thumb, FTYPE)
            temp_thumb.seek(0)

            thumb_data = InMemoryUploadedFile(
                temp_thumb,
                None,
                thumb_filename,
                f"image/{FTYPE.lower()}",
                temp_thumb.tell(),
                None,
            )

            thumbnail_custom.thumbnail_custom = thumb_data

            return True

        return False

    def get_remaining_time_and_set_expiration(self):

        if self.expiration_time:
            elapsed_time = timezone.now() - self.created
            remaining_time = self.expiration_time - elapsed_time.total_seconds()
            if remaining_time < 0:
                remaining_time = 0
                self.expiration = True
                self.save()
                return "This image has expired"
            return remaining_time
        return None

    def get_remaining_time_and_set_expiration_expiring_seconds(self):

        if self.expiring_seconds:
            elapsed_time = timezone.now() - self.created
            remaining_time = self.expiring_seconds - elapsed_time.total_seconds()
            if remaining_time < 0:
                remaining_time = 0
                return "This image has expired"
            return remaining_time
        return None
