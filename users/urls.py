from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterAPIView, LogoutAPIView, ChangePasswordAPIView, ResetPasswordRequestAPIView, \
    ResetPasswordConfirmAPIView, VerifyAPIView

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='register'),
    path('auth/verify/', VerifyAPIView.as_view(), name='verify'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('auth/reset-password-request/', ResetPasswordRequestAPIView.as_view(), name='reset-password-request'),
    path('auth/reset-password-confirm/', ResetPasswordConfirmAPIView.as_view(), name='reset-password-confirm'),


]
