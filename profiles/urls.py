from django.urls import path

from profiles.views import ProfileListAPIView, ProfileDetailAPIView, MyProfileAPIView, AvatarUpdateView

urlpatterns = [
    path('profiles/', ProfileListAPIView.as_view(), name='profile-list'),
    path('profiles/<uuid:profile_id>/', ProfileDetailAPIView.as_view(), name='profile-detail'),
    path('profiles/me/', MyProfileAPIView.as_view(), name='profile-update'),
    path('profiles/avatar/', AvatarUpdateView.as_view(), name='avatar-update'),

]
