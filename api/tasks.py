import os
import logging
import uuid
import time
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from celery import shared_task
from django.conf import settings


# r = redis.Redis(host="localhost", port=6379, db=0)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@shared_task
def generate_thumbnail(uploaded_image_name, account_tier, width=None, height=None):
    from .models import Images, Thumbnail, UserProfile

    time.sleep(0.5)
    get_author = Images.objects.get(image=uploaded_image_name)
    is_super_user = get_author.author.userprofile.user.is_superuser

    sizes = []

    logger.debug(
        f"""Task generate_thumbnail {uploaded_image_name}
        account type {account_tier}
        is super user = {is_super_user}:{width}:{height}:{sizes}"""
    )

    file_path = os.path.join(settings.MEDIA_ROOT, f"{uploaded_image_name}")
    if account_tier == UserProfile.BASIC:
        sizes.append((200, 200))
    elif account_tier in [UserProfile.PREMIUM, UserProfile.ENTERPRISE]:
        sizes.append((200, 200))
        sizes.append((400, 400))
        if is_super_user == True:
            sizes.append((width, height))
    logger.debug(f"Added to sizes {sizes}")

    if not os.path.exists(file_path):
        logger.error(f"File {file_path} does not exist")
        return False

    try:
        # Add delay to allow time for image to be fully saved to database
        time.sleep(1)

        with open(file_path, "rb") as file:
            image = Image.open(file)
            thumbnail = Thumbnail()

            for i, size in enumerate(sizes):
                thumb_name = uuid.uuid4().hex
                thumb_extension = os.path.splitext(uploaded_image_name)[1]
                thumb_filename = f"{thumb_name}_thumb_{i}{thumb_extension}"

                if thumb_extension in [".jpg", ".jpeg"]:
                    FTYPE = "JPEG"
                elif thumb_extension == ".gif":
                    FTYPE = "GIF"
                elif thumb_extension == ".png":
                    FTYPE = "PNG"
                else:
                    return False  # Unrecognized file type

                # Save thumbnail to in-memory file as BytesIO
                temp_thumb = BytesIO()
                image_copy = image.copy()
                # image_copy.thumbnail(size)

                if size[0] is not None and size[1] is not None:
                    # logger.error(f"Size {size} checker {size[0]} {size[1]}:::size i {size[i]}")
                    image_copy.thumbnail(size)
                image_copy.save(temp_thumb, FTYPE)
                temp_thumb.seek(0)

                # Create an InMemoryUploadedFile from the bytes data of the thumbnail
                thumb_data = InMemoryUploadedFile(
                    temp_thumb,
                    None,
                    thumb_filename,
                    f"image/{FTYPE.lower()}",
                    temp_thumb.tell(),
                    None,
                )
                if i == 0:
                    thumbnail.thumbnail_200 = thumb_data
                elif i == 1:
                    thumbnail.thumbnail_400 = thumb_data
                elif i == 2 and size[0] is not None and size[1] is not None:
                    thumbnail.thumbnail_custom = thumb_data

            # Save thumbnail to database
            thumbnail.save()
            images_obj = Images.objects.get(image=uploaded_image_name)
            images_obj.thumbnail = thumbnail
            images_obj.save()

            logger.debug(
                f"Image object get {images_obj} Images thumbnail {images_obj.thumbnail}"
            )

    except:
        logger.exception(f"Error generating thumbnail for file {file_path}")
