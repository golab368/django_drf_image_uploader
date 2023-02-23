from rest_framework import serializers
from django.utils.text import slugify
from .models import UserProfile, Images, Thumbnail, ThumbnailCustom
from django.utils import timezone


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "user", "account_type"]


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["thumbnail_200", "thumbnail_400"]


class ImagesSerializer(serializers.ModelSerializer):
    thumbnail_200 = serializers.SerializerMethodField()
    thumbnail_400 = serializers.SerializerMethodField()
    author = serializers.ReadOnlyField(source="author.username")

    def __init__(self, *args, **kwargs):

        user = kwargs["context"]["request"].user
        if user.userprofile.account_type in [UserProfile.PREMIUM, UserProfile.BASIC]:
            self.fields.pop("expiration_time", None)
        super().__init__(*args, **kwargs)

    def get_thumbnail_200(self, obj):
        if obj.thumbnail and obj.thumbnail.thumbnail_200:
            return self.context["request"].build_absolute_uri(
                obj.thumbnail.thumbnail_200.url
            )
        return None

    def get_thumbnail_400(self, obj):
        if obj.thumbnail and obj.thumbnail.thumbnail_400:
            return self.context["request"].build_absolute_uri(
                obj.thumbnail.thumbnail_400.url
            )
        return None

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    class Meta:
        model = Images
        fields = (
            "title",
            "image",
            "slug",
            "created",
            "author",
            "expiration_time",
            "thumbnail_200",
            "thumbnail_400",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.expiration_time:
            elapsed_time = timezone.now() - instance.created
            remaining_time = instance.expiration_time - elapsed_time.total_seconds()
            if remaining_time < 0:
                remaining_time = 0
                data["expiration"] = True
                data["image"] = "http://127.0.0.1:8000/media/expired.png"
                data["original_file_link"] = "http://127.0.0.1:8000/media/expired.png"
                data["thumbnail_200"] = "http://127.0.0.1:8000/media/expired.png"
                data["thumbnail_400"] = "http://127.0.0.1:8000/media/expired.png"
            else:
                data["remaining_time"] = remaining_time
        return data
