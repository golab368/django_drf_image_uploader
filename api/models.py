import uuid
from django.contrib.auth.models import AbstractUser
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
    NONE = "None"
    ACCOUNT_TIERS = (
        (BASIC, "Basic"),
        (PREMIUM, "Premium"),
        (ENTERPRISE, "Enterprise"),
        (NONE, "None"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=255, choices=ACCOUNT_TIERS)

    def __str__(self):
        return self.user.username


class Thumbnail(models.Model):
    thumbnail_200 = models.ImageField(null=True, blank=True)
    thumbnail_400 = models.ImageField(null=True, blank=True)
    thumbnail_custom = models.ImageField(null=True, blank=True)


class Images(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to=user_directory_path)
    slug = models.SlugField(max_length=250, null=True, blank=True)
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

    def delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def save(self, *args, **kwargs):

        # Get values from admin panel
        self.width = kwargs.pop("width", None)
        self.height = kwargs.pop("height", None)
        # Set the title and slug based on the image file name
        self.title = self.image.name
        self.slug = slugify(self.title)
        if self.image:
            self.original_file_link = self.image

        # Set the expiration time to 24 hours after creation if not already set
        if not self.expiration_time:
            if type(self.expiring_seconds) != int:
                self.expiring_seconds = 86400
            elif self.expiring_seconds > 86400:
                self.expiring_seconds = 86400

        user_profile = UserProfile.objects.get(user=self.author)
        account_tier = user_profile.account_type
        # self.thumbnail_queued = True

        super().save(*args, **kwargs)

        if not self.thumbnail and self.width is not None and self.height is not None:
            if not getattr(self, "thumbnail_queued", False):
                generate_thumbnail.delay(
                    self.image.name, account_tier, width=self.width, height=self.height
                )
                self.thumbnail_queued = True
        elif not self.thumbnail and self.width is None and self.height is None:

            if not getattr(self, "thumbnail_queued", False):
                generate_thumbnail.delay(self.image.name, account_tier)
                self.thumbnail_queued = True

    def get_remaining_time_and_set_expiration(self, exp_time):

        if exp_time:
            elapsed_time = timezone.now() - self.created
            remaining_time = float(exp_time) - elapsed_time.total_seconds()
            if remaining_time <= 0:
                # remaining_time = 0
                self.expiration = True
                self.save()
                self.delete()
                return "This image has expired and was deleted"
            return remaining_time
        return None

    def get_expiration_time(self, exp_time=0):
        return self.get_remaining_time_and_set_expiration(exp_time)

    def get_expiring_seconds(self, exp_time=0):
        return self.get_remaining_time_and_set_expiration(exp_time)
