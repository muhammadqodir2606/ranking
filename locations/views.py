from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from locations.models import City, Country
from locations.pagination import CityPagination
from locations.serializers import CitySerializer, CountrySerializer


class CityListAPIView(APIView):
    serializer_class = CitySerializer

    def get(self, request):
        country_id = request.query_params.get("country")
        search = request.query_params.get("search")
        qs = City.objects.all()
        if country_id:
            qs = City.objects.select_related("country")

        if country_id:
            qs = qs.filter(country_id=country_id)

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
            )

        qs = qs.order_by(
            "name",
            'id'
        )

        paginator = CityPagination()
        page = paginator.paginate_queryset(qs, request)

        serializer = self.serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CountryListAPIView(APIView):
    serializer_class = CountrySerializer

    def get(self, request):
        search = request.query_params.get("search")

        qs = Country.objects.all()

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
            )

        qs = qs.order_by(
            "name",
            "id"
        )

        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data, status=200)
