from django.urls import path, include
from rest_framework import routers
from train_station_system.views import (
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    JourneyViewSet,
    OrderViewSet,
    TrainTypeViewSet,
    TicketViewSet
)

router = routers.DefaultRouter()
router.register("crew", CrewViewSet)
router.register("station", StationViewSet)
router.register("route", RouteViewSet)
router.register("train", TrainViewSet)
router.register("journey", JourneyViewSet)
router.register("order", OrderViewSet)
router.register("train_type", TrainTypeViewSet)
router.register("ticket", TicketViewSet)
urlpatterns = [
    path("", include(router.urls)),
]
app_name = "train_station_system"
