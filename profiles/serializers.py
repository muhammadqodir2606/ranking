from users.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from locations.models import City
from locations.serializers import CitySerializer
from profiles.models import Profile


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username')


class ProfileSerializer(ModelSerializer):
    user = UserSerializer()
    city = CitySerializer()
    me_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "avatar",
            "user",
            "city",
            "likes_count",
            "views_count",
            "popularity_score",
            "created_time",
            "me_liked",
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="user.first_name",
        required=False
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False
    )
    username = serializers.CharField(
        source="user.username",
        required=True
    )
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Profile
        fields = (
            "city",
            "username",
            "first_name",
            "last_name",
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        return super().update(instance, validated_data)


class AvatarUpdateSerializer(ModelSerializer):
    avatar = serializers.ImageField(use_url=False)

    class Meta:
        model = Profile
        fields = ("avatar",)

    def validate_avatar(self, value):
        if value.size > 10 * 1024 * 1024:
            raise ValidationError("File should not be larger than 10 MB.")
        return value
