import os
from django.apps import AppConfig
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Images


@receiver(post_delete, sender=Images)
def delete_image(sender, instance, **kwargs):
    """
    Deletes the image file associated with an Image instance
    """
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

    if instance.thumbnail and instance.thumbnail.id is not None:
        if instance.thumbnail.thumbnail_200 and os.path.isfile(
            instance.thumbnail.thumbnail_200.path
        ):
            os.remove(instance.thumbnail.thumbnail_200.path)
        if instance.thumbnail.thumbnail_400 and os.path.isfile(
            instance.thumbnail.thumbnail_400.path
        ):
            os.remove(instance.thumbnail.thumbnail_400.path)
        if instance.thumbnail.thumbnail_custom and os.path.isfile(
            instance.thumbnail.thumbnail_custom.path
        ):
            os.remove(instance.thumbnail.thumbnail_custom.path)

        instance.thumbnail.delete()


