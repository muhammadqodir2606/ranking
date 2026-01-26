from django.contrib import admin
from .models import Country, City


@admin.register(Country)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
    )
    search_fields = ("name", "code")
    ordering = ("name", )


admin.site.register(City)
