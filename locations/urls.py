from django.urls import path

from locations.views import CityListAPIView, CountryListAPIView

urlpatterns = [
    path('cities/', CityListAPIView.as_view(), name='cities-list'),
    path('countries/', CountryListAPIView.as_view(), name='countries-list')
]
