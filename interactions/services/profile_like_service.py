from django.db import transaction, IntegrityError
from django.db.models import F
from django.db.models.functions import Greatest
from interactions.models import ProfileLike
from profiles.models import Profile


class ProfileLikeService:

    @staticmethod
    @transaction.atomic
    def like(*, to_profile, from_profile):

        if to_profile.id == from_profile.id:
            raise ValueError("Cannot like your own profile")

        try:
            like, created = ProfileLike.objects.get_or_create(
                to_profile=to_profile,
                from_profile=from_profile
            )
        except IntegrityError:
            return {"liked": True}

        if not created:
            like.delete()

            Profile.objects.filter(id=to_profile.id).update(
                likes_count=Greatest(F('likes_count') - 1, 0),
                popularity_score=F('popularity_score') - 5
            )
            return {"liked": False}

        Profile.objects.filter(id=to_profile.id).update(
            likes_count=F('likes_count') + 1,
            popularity_score=F('popularity_score') + 5
        )

        return {"liked": True}
