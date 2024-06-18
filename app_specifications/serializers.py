from rest_framework import serializers

from app_specifications.models import (
    Specifications,
    NameSpecifications,
    ValueSpecifications,
)


class NameSpecificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NameSpecifications
        fields = "__all__"


class ValueSpecificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueSpecifications
        fields = "__all__"


class SpecificationsSerializer(serializers.ModelSerializer):
    name_specification = NameSpecificationsSerializer()
    value_specification = ValueSpecificationsSerializer()

    class Meta:
        model = Specifications
        fields = "__all__"
