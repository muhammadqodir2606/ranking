from django.contrib import admin
from .models import ProfileLike, ProfileView


@admin.register(ProfileLike)
class ProfileLikeAdmin(admin.ModelAdmin):
    readonly_fields = ("to_profile", "from_profile", "created_time")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ("to_profile", "from_profile", "created_time")
    readonly_fields = ("to_profile", "from_profile", "created_time")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
