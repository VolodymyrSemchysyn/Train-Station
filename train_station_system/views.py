from datetime import datetime

from django.db.models import F, Count
from rest_framework import viewsets, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet

from train_station_system.models import Crew, Station, Route, Order, Train, Journey, TrainType, Ticket
from train_station_system.serializers import (
    CrewSerializer,
    StationSerializer,
    RouteSerializer,
    OrderSerializer,
    TrainSerializer,
    TrainListSerializer,
    JourneySerializer,
    JourneyCreateSerializer,
    OrderListSerializer,
    TrainTypeSerializer,
    TicketListSerializer
)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class RouteViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet
                   ):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Train.objects.select_related("train_type")

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        return TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all().select_related("route", "train").prefetch_related("crew")

    # permission_classes = (IsAuthenticated,)

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        train_id = self.request.query_params.get("train")
        queryset = self.queryset

        if source:
            queryset = queryset.filter(route__source=source)

        if destination:
            queryset = queryset.filter(route__destination=destination)

        if train_id:
            try:
                train = Train.objects.get(id=train_id)
                queryset = queryset.filter(train=train)
            except Train.DoesNotExist:
                raise ValidationError({"train": "Train does not exist."})

        queryset = queryset.annotate(
            available_seats=F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets")
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneySerializer

        return JourneyCreateSerializer


class OrderPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Order.objects.select_related("user").prefetch_related("tickets")
    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TicketViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Ticket.objects.select_related("order", "journey")
    serializer_class = TicketListSerializer
