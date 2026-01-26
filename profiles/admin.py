from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "country",
        "city",
        "popularity_score",
        "likes_count",
        "views_count",
        "created_time",
    )
