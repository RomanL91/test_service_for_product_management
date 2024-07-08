from rest_framework import serializers

from app_services.models import Service

from app_sales_points.serializers import CitySerializer


class ServiceSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = Service
        fields = "__all__"
