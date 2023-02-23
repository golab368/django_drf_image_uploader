from django.contrib import admin
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from django.utils.html import format_html
from io import BytesIO
from PIL import Image

from .models import Images, UserProfile, ThumbnailCustom, User
from django.conf import settings


class ImagesForm(forms.ModelForm):
    thumbnail_width = forms.IntegerField(
        required=False, label="Thumbnail Width (in pixels)"
    )
    thumbnail_height = forms.IntegerField(
        required=False, label="Thumbnail Height (in pixels)"
    )
    expiring_seconds = forms.IntegerField(
        required=False, label="Expiring seconds (between 300 and 30000)"
    )

    class Meta:
        model = Images
        fields = "__all__"


class ImagesAdmin(admin.ModelAdmin):
    form = ImagesForm
    list_display = (
        "id",
        "title",
        "get_original_file_link_html",
        "created",
    )

    def save_model(self, request, obj, form, change):
        thumbnail_width = form.cleaned_data.get("thumbnail_width")
        thumbnail_height = form.cleaned_data.get("thumbnail_height")

        if thumbnail_width is not None and thumbnail_height is not None:
            if obj.make_thumbnail_custom(thumbnail_width, thumbnail_height):
                thumbnail_custom = ThumbnailCustom.objects.create()
                thumbnail_custom.save()
                obj.thumbnail_custom = thumbnail_custom
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj and obj.thumbnail_custom:
            fields += ("thumbnail_custom",)
        return fields

    def get_original_file_link_html(self, obj):
        """
        Return an HTML link to the originally uploaded file that expires after a number of seconds.
        """
        if obj.original_file_link:
            remaining_time = (
                obj.get_remaining_time_and_set_expiration_expiring_seconds()
            )
            if remaining_time != None and remaining_time != "":
                remaining_time = int(remaining_time)
                if remaining_time <= 0:
                    return "Link has expired"
                return format_html(
                    '<a href="{}?expires={}" target="_blank">View original file (expires in {} seconds)</a>',
                    reverse("original_file_link", args=[obj.id]),
                    remaining_time,
                    remaining_time,
                )
            else:
                return "Expiring link not provided"
        else:
            return "No original file uploaded."

    get_original_file_link_html.short_description = "Original File"


admin.site.register(Images, ImagesAdmin)
admin.site.register(UserProfile)
admin.site.register(User)
