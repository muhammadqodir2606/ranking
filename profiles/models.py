from django.core.validators import FileExtensionValidator
from django.db import models
from users.models import User

from locations.models import Country, City
from shared.models import BaseModel


class Profile(BaseModel):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[
        FileExtensionValidator(['jpg', 'png', 'heic', 'heif', 'jpeg'])
    ])
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    country = models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    city = models.ForeignKey(
        City,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    likes_count = models.PositiveIntegerField(editable=False, default=0)
    views_count = models.PositiveIntegerField(editable=False, default=0)
    popularity_score = models.PositiveIntegerField(editable=False, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
