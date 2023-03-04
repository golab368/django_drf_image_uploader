from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from .models import UserProfile, Images, Thumbnail
from django.utils import timezone


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "user", "account_type"]


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["thumbnail_200", "thumbnail_400", "thumbnail_custom"]


class ImagesSerializer(serializers.ModelSerializer):
    thumbnail_200 = serializers.SerializerMethodField()
    thumbnail_400 = serializers.SerializerMethodField()
    thumbnail_custom = serializers.SerializerMethodField()
    author = serializers.ReadOnlyField(source="author.username")
    expiring_seconds = serializers.IntegerField(write_only=True, required=False)

    # def __init__(self, *args, **kwargs):

    #     user = kwargs["context"]["request"].user

    #     try:
    #         account_type = user.userprofile.account_type
    #     except:
    #         UserProfile.objects.create(user=user, account_type="None")
    #         account_type = user.userprofile.account_type

    #     if account_type in [UserProfile.PREMIUM, UserProfile.BASIC]:
    #         self.fields.pop("expiration_time", None)
    #         self.fields.pop("expiration", None)
    #         self.fields.pop("expiring_seconds", None)
    #     elif account_type == UserProfile.ENTERPRISE:
    #         self.fields.pop("expiring_seconds", None)
    #         self.fields.pop("expiration", None)
    #         self.fields.pop("thumbnail_custom", None)
    #     elif account_type == UserProfile.NONE:
    #         print("dasdaosjdioasdioe12ue812e12i")
    #         for field_name in self.fields:
    #             self.fields[field_name].read_only = True
    #     super().__init__(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        if user.is_authenticated and not user.is_superuser:
            try:
                account_type = user.userprofile.account_type
                if account_type == UserProfile.NONE:
                    for field_name in self.fields:
                        self.fields[field_name].read_only = True
                    # self.fields.pop("title", None)
                    # self.fields.pop("slug", None)
                    # self.fields.pop("created", None)
                    # self.fields.pop("author", None)
                    # self.fields.pop("image", None)
                    # self.fields.pop("expiration", None)
                    # # self.fields.pop("expiring_time", None)
                    # # self.fields.pop("expiring_seconds", None)
                    # self.fields.pop("thumbnail_200", None)
                    # self.fields.pop("thumbnail_400", None)
                    # self.fields.pop("thumbnail_custom", None)
                elif account_type == UserProfile.BASIC:
                    self.fields.pop("expiration_time", None)
                    # self.fields.pop("expiration", None)
                    self.fields.pop("expiring_seconds", None)
                    # self.fields.pop("thumbnail_200", None)
                    self.fields.pop("thumbnail_400", None)
                    self.fields.pop("thumbnail_custom", None)
                elif account_type == UserProfile.PREMIUM:
                    self.fields.pop("expiration_time", None)
                    self.fields.pop("thumbnail_custom", None)
                    self.fields.pop("expiring_seconds", None)
                    # self.fields.pop("expiration", None)
                elif account_type == UserProfile.ENTERPRISE:
                    self.fields.pop("expiring_seconds", None)

                else:
                    raise serializers.ValidationError(
                        "Invalid account type. Contact support."
                    )
            except:
                UserProfile.objects.create(user=user, account_type="None")

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

    def get_thumbnail_custom(self, obj):
        if obj.thumbnail and obj.thumbnail.thumbnail_custom:
            return self.context["request"].build_absolute_uri(
                obj.thumbnail.thumbnail_custom.url
            )
        return None

    # def create(self, validated_data):
    #     # set expiration time to 1 day

    #     validated_data["author"] = self.context["request"].user
    #     return super().create(validated_data)

    def create(self, validated_data):
        user = self.context["request"].user
        if not user.is_authenticated:
            raise serializers.ValidationError("User is not authenticated.")

        elif user.is_superuser:
            image = Images.objects.create(**validated_data)
        else:
            account_type = user.userprofile.account_type
            if account_type == UserProfile.NONE:
                raise serializers.ValidationError(
                    "User does not have permission to create images."
                )
            elif account_type == UserProfile.BASIC:
                self.fields.pop("expiration_time", None)
                self.fields.pop("expiration", None)
                self.fields.pop("expiring_seconds", None)
                self.fields.pop("thumbnail_400", None)
                self.fields.pop("thumbnail_custom", None)
            elif account_type == UserProfile.PREMIUM:
                self.fields.pop("thumbnail_custom", None)

            elif account_type == UserProfile.ENTERPRISE:
                self.fields.pop("expiring_seconds", None)

            image = Images.objects.create(**validated_data)

        return image

    class Meta:
        model = Images
        fields = (
            "title",
            "image",
            "slug",
            "created",
            "author",
            # "expiration",
            "expiration_time",
            "thumbnail_200",
            "thumbnail_400",
            "thumbnail_custom",
            "expiring_seconds",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance and self.context["request"].user.is_superuser:
            if instance.expiration_time:
                remaining_time = instance.get_expiration_time(instance.expiration_time)
                data["remaining_time"] = remaining_time
                data["expiring_seconds"] = instance.expiration_time
            elif instance.expiring_seconds:
                remaining_time = instance.get_expiring_seconds(
                    instance.expiring_seconds
                )
                data["remaining_time"] = remaining_time
                data["expiring_seconds"] = instance.expiring_seconds
                # elapsed_time = timezone.now() - instance.created
                # remaining_time = float(exp) - elapsed_time.total_seconds()
                # if isinstance(remaining_time, int) and remaining_time <= 0:
                #     #remaining_time = 0
                #     data["expiration"] = True
                #     data["image"] = "http://127.0.0.1:8000/media/expired.png"
                #     data[
                #         "original_file_link"
                #     ] = "http://127.0.0.1:8000/media/expired.png"
                #     data["thumbnail_200"] = "http://127.0.0.1:8000/media/expired.png"
                #     data["thumbnail_400"] = "http://127.0.0.1:8000/media/expired.png"
                #     data["thumbnail_custom"] = "http://127.0.0.1:8000/media/expired.png"
                # else:
                # data["remaining_time"] = remaining_time

        else:
            if instance.expiration_time:
                remaining_time = instance.get_expiration_time(instance.expiration_time)
                data["remaining_time"] = remaining_time
                data["expiring_seconds"] = instance.expiration_time
        return data
