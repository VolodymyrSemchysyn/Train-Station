from rest_framework import serializers

from train_station_system.models import Crew, Train, TrainType, Order


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("first_name", "last_name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = TrainType(read_only=True)

    class Meta:
        model = Train
        fields = (
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type"
        )


class TrainListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "train_type")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("name",)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("created_at",)