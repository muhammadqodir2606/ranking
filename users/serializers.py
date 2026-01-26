from users.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])
    username = serializers.CharField(validators=[])

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_email(self, value):
        value = value.lower()
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class VerifySerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        if not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError("User not found")
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data["new_password"] == data["old_password"]:
            raise serializers.ValidationError("New password don't match old password.")
        return data


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User not found")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
