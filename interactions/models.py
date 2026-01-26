from users.models import User
from django.db import models
from profiles.models import Profile
from shared.models import BaseModel


class ProfileLike(BaseModel):
    from_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="given_likes"
    )

    to_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="received_likes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_profile", "to_profile"],
                name="unique_profile_like"
            )
        ]

    def __str__(self):
        return f"{self.from_profile} -> {self.to_profile}"


class ProfileView(BaseModel):
    to_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="views",
        null=True,
        blank=True
    )

    from_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["to_profile", "from_profile"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["from_profile", "to_profile"],
                name="unique_profile_view_user"
            ),
        ]

    def delete(self, *args, **kwargs):
        raise RuntimeError("Profile view cannot be deleted")

    def __str__(self):
        return f"{self.from_profile.user.username} viewed {self.to_profile.user.username}"

