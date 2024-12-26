from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from train_station_system.models import (
    Crew,
    Train,
    TrainType,
    Order,
    Journey,
    Ticket,
    Route,
    Station
)


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ("full_name",)

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("name",)


class TrainSerializer(serializers.ModelSerializer):
    train_type = TrainTypeSerializer(read_only=True)

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


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("source", "destination", "distance")


class JourneySerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    train = serializers.StringRelatedField(read_only=True)
    crew = CrewSerializer(read_only=True, many=True)

    class Meta:
        model = Journey
        fields = (
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        )


class JourneyCreateSerializer(JourneySerializer):
    route = serializers.PrimaryKeyRelatedField(queryset=Route.objects.all())
    train = serializers.PrimaryKeyRelatedField(queryset=Train.objects.all())
    crew = serializers.PrimaryKeyRelatedField(queryset=Crew.objects.all(), many=True)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")


class TicketListSerializer(TicketSerializer):
    journey = JourneySerializer(read_only=True, many=False)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("name", "latitude", "longitude")
