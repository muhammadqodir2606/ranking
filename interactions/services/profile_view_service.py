from django.db import transaction, IntegrityError
from django.db.models import F
from interactions.models import ProfileView
from profiles.models import Profile


class ProfileViewService:

    @staticmethod
    @transaction.atomic
    def add_view(*, to_profile, from_profile):
        if to_profile.id == from_profile.id:
            return

        try:
            ProfileView.objects.create(
                to_profile=to_profile,
                from_profile=from_profile
            )
        except IntegrityError:
            return

        Profile.objects.filter(id=to_profile.id).update(
            views_count=F('views_count') + 1,
            popularity_score=F('popularity_score') + 1
        )


