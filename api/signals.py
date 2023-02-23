# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Images
# from .tasks import generate_thumbnail

# @receiver(post_save, sender=Images)
# def generate_thumbnail_on_save(sender, instance, **kwargs):
#     generate_thumbnail.delay(instance.id, instance.image.name)