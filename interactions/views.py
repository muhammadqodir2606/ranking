from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from interactions.services.profile_like_service import ProfileLikeService
from interactions.services.profile_view_service import ProfileViewService
from profiles.models import Profile


class ProfileViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, profile_id):
        to_profile = get_object_or_404(Profile, pk=profile_id)
        from_profile = request.user.profile

        ProfileViewService.add_view(
            to_profile=to_profile,
            from_profile=from_profile
        )

        return Response({"viewed": True})


class ProfileLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, profile_id):
        to_profile = get_object_or_404(Profile, pk=profile_id)
        from_profile = request.user.profile

        try:
            result = ProfileLikeService.like(
                to_profile=to_profile,
                from_profile=from_profile
            )
        except ValueError:
            return Response(
                {"detail": "You cannot like your own profile"},
                status=400
            )

        return Response(result)
