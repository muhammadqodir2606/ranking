from django.db.models import Exists, OuterRef, Q, Value, BooleanField
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from interactions.models import ProfileLike
from .models import Profile
from .pagination import ProfilePagination
from .serializers import ProfileSerializer, ProfileUpdateSerializer, AvatarUpdateSerializer


class ProfileDetailAPIView(APIView):
    serializer_class = ProfileSerializer

    def get(self, request, profile_id):
        user = request.user

        qs = Profile.objects.filter(
            id=profile_id,
            is_active=True,
            user__is_active=True
        )

        if user.is_authenticated and hasattr(user, "profile"):
            qs = qs.annotate(
                me_liked=Exists(
                    ProfileLike.objects.filter(
                        from_profile=user.profile,
                        to_profile=OuterRef("pk")
                    )
                )
            )
        else:
            qs = qs.annotate(
                me_liked=Value(False, output_field=BooleanField())
            )

        profile = get_object_or_404(qs)

        serializer = self.serializer_class(profile, context={"request": request})
        return Response(serializer.data)


class ProfileListAPIView(APIView):
    serializer_class = ProfileSerializer

    def get(self, request):
        qs = Profile.objects.filter(
            is_active=True,
            user__is_active=True
        ).select_related(
            "user",
            "city",
            "city__country",
        )

        country = request.query_params.get("country")
        city = request.query_params.get("city")
        search = request.query_params.get("search")
        order = request.query_params.get("order", "popularity")

        if country:
            qs = qs.filter(city__country_id=country)

        if city:
            qs = qs.filter(city_id=city)

        if search:
            qs = qs.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(city__name__icontains=search)
            )

        user = request.user

        if user.is_authenticated and hasattr(user, "profile"):
            qs = qs.annotate(
                me_liked=Exists(
                    ProfileLike.objects.filter(
                        from_profile=user.profile,
                        to_profile=OuterRef("pk")
                    )
                )
            )
        else:
            qs = qs.annotate(
                me_liked=Value(False, output_field=BooleanField())
            )

        if order == "popularity":
            qs = qs.order_by(
                "-popularity_score",
                "-likes_count",
                "-views_count",
                "id"
            )
        else:
            qs = qs.order_by(
                "-created_time"
            )

        paginator = ProfilePagination()
        page_obj = paginator.paginate_queryset(qs, request)

        serializer = self.serializer_class(
            page_obj,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)


class AvatarUpdateView(GenericAPIView):
    serializer_class = AvatarUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        serializer = self.get_serializer(
            instance=request.user.profile,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyProfileAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProfileSerializer
        return ProfileUpdateSerializer

    def get(self, request):
        serializer = self.get_serializer(
            instance=request.user.profile,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = self.get_serializer(
            instance=request.user.profile,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


    # @extend_schema(responses=ProfileSerializer)
    # def get(self, request):
    #     profile = request.user.profile
    #     serializer = ProfileSerializer(
    #         profile,
    #         context={"request": request}
    #     )
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # @extend_schema(responses=ProfileUpdateSerializer)
    # def put(self, request):
    #     serializer = ProfileUpdateSerializer(
    #         request.user.profile,
    #         data=request.data,
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)