from rest_framework import serializers

from train_station_system.models import Crew, Train, TrainType, Order, Journey, Ticket, Route, Station


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


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
    )

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")

    def validate_tickets(self, tickets):
        for ticket_data in tickets:
            cargo = ticket_data.get("cargo")
            seat = ticket_data.get("seat")
            journey_id = ticket_data.get("journey_id")

            if not all([cargo, seat, journey_id]):
                raise serializers.ValidationError("All fields 'cargo', 'seat' and 'journey_id' are required.")

            try:
                journey = Journey.objects.get(id=journey_id)
            except Journey.DoesNotExist:
                raise serializers.ValidationError(f"Journey id={journey_id} does not exist.")

            if Ticket.objects.filter(cargo=cargo, seat=seat, journey=journey).exists():
                raise serializers.ValidationError(
                    f"Ticket is not available."
                )

            Ticket.validate_ticket(cargo, seat, journey.train)

        return tickets

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)

        for ticket_data in tickets_data:
            Ticket.objects.create(
                cargo=ticket_data["cargo"],
                seat=ticket_data["seat"],
                journey_id=ticket_data["journey_id"],
                order=order,
            )

        return order


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("source", "destination", "distance")


class JourneySerializer(serializers.ModelSerializer):
    route = RouteSerializer(read_only=True)
    train = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        )


class TicketSerializer(serializers.ModelSerializer):
    journey = JourneySerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")
