from django.urls import path

from interactions.views import ProfileViewAPIView, ProfileLikeAPIView

urlpatterns = [
    path("interactions/<uuid:profile_id>/view/", ProfileViewAPIView.as_view()),
    path("interactions/<uuid:profile_id>/like/", ProfileLikeAPIView.as_view()),
]
