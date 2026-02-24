from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .tasks import send_mail
from .models import User
from .serializers import (RegisterSerializer, LogoutSerializer, ChangePasswordSerializer,
                          ResetPasswordRequestSerializer, PasswordResetConfirmSerializer, VerifySerializer)
from .tokens import EmailVerificationTokenGenerator
from django.core.cache import cache

RATE_LIMIT_SECONDS = 60
redis = get_redis_connection("default")


class RegisterAPIView(APIView):
    authentication_classes = []
    serializer_class = RegisterSerializer
    
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email or user_by_username:
            user = user_by_email or user_by_username

            if user_by_email and user_by_username and user_by_email.id != user_by_username.id:
                return Response(
                    {
                        'message': 'Email and username already in use'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user.is_verified:
                return Response(
                    {
                        'message': 'User already exist'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.serializer_class(
                instance=user,
                data=request.data
            )
        else:
            serializer = self.serializer_class(
                data=request.data
            )

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = EmailVerificationTokenGenerator().make_token(user)

        redis_key = f"email_verify:{user.id}"
        redis.setex(
            redis_key,
            15*60,
            token
        )

        verify_url = (
            f"https://frontend.com/verify-email/"
            f"?uuid={user.id}&token={token}"
        )

        cache_key = f"register:email:{email}"
        if cache.get(cache_key):
            return Response(
                {
                    "message": "Verification already sent, please wait."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        send_mail.delay(
            subject="Confirm email",
            email=user.email,
            template_name="emails/verify_email.html",
            context={
                "verify_url": verify_url
            }
        )
        cache.set(cache_key, 1, timeout=RATE_LIMIT_SECONDS)
        return Response(
            {
                "message": "Verification link sent to your email"
            },
            status=status.HTTP_200_OK
        )


class VerifyAPIView(APIView):
    authentication_classes = []
    serializer_class = VerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, id=serializer.validated_data.get('user_id'))
        token = serializer.validated_data.get('token')

        redis_key = f"email_verify:{user.id}"
        saved_token = redis.get(redis_key)

        if not saved_token:
            return Response(
                {
                    "message": "Token expired"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if saved_token.decode() != token:
            return Response(
                {
                    "message": "Invalid token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not EmailVerificationTokenGenerator().check_token(user, token):
            return Response(
                {
                    "message": "Invalid or expired token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        redis.delete(redis_key)
        user.is_verified = True
        user.is_active = True
        user.save()
        return Response(
            {
                "message": "Verification is successful"
            }
        )


class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success": True,
                "message": "Successfully logged out"
            }
            return Response(data, status=status.HTTP_200_OK)
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()

        return Response({"success": True}, status=status.HTTP_200_OK)


class ResetPasswordRequestAPIView(APIView):
    serializer_class = ResetPasswordRequestSerializer
    authentication_classes = []
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        token = PasswordResetTokenGenerator().make_token(user)

        redis_key = f"reset_password:{user.id}"
        redis.setex(
            redis_key,
            15 * 60,
            token
        )

        cache_key = f"reset_password:email:{user.email}"
        if cache.get(cache_key):
            return Response(
                {
                    "message": "Verification already sent, please wait."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        reset_url = (
            f"https://frontend.com/reset-password/"
            f"?uuid={user.id}&token={token}"
        )

        send_mail.delay(
            subject="Password Reset ",
            email=user.email,
            template_name="emails/reset_password.html",
            context={
                "reset_url": reset_url
            }
        )
        cache.set(cache_key, 1, timeout=RATE_LIMIT_SECONDS)

        return Response(
            {
                "message": "Password reset link sent"
            },
            status=status.HTTP_200_OK
        )


class ResetPasswordConfirmAPIView(APIView):
    serializer_class = PasswordResetConfirmSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, id=serializer.validated_data["user_id"])
        token = serializer.validated_data["token"]

        redis_key = f"reset_password:{user.id}"

        saved_token = redis.get(redis_key)

        if not saved_token:
            return Response(
                {
                    "message": "Token expired"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if saved_token.decode() != token:
            return Response(
                {
                    "message": "Invalid token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response(
                {
                    "message": "Invalid or expired token"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        redis.delete(redis_key)
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {
                "message": "Password updated successfully"
            },
            status=status.HTTP_200_OK
        )
