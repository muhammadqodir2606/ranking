from rest_framework.serializers import ModelSerializer

from locations.models import Country, City


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', 'code')


class CitySerializer(ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = City
        fields = ('id', 'name', 'country')
