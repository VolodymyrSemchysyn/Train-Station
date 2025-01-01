import os
import tempfile
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient
from train_station_system.models import Train, TrainType, Ticket, Journey
from train_station_system.serializers import TrainListSerializer, RouteSerializer
from train_station_system.models import Route, Station

TRAIN_URL = reverse("train_station_system:train-list")
JOURNEY_URL = reverse("train_station_system:journey-list")


def sample_train(**params):
    train_type = TrainType.objects.create(name="Freight")
    defaults = {
        "name": "Train 1",
        "cargo_num": 100,
        "places_in_cargo": 50,
        "train_type": train_type
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_ticket(**params):
    defaults = {
        "cargo": 1,
        "seat": 1,
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


def sample_route(**params):
    source = Station.objects.create(name="Station A", latitude=12.34, longitude=56.78)
    destination = Station.objects.create(name="Station B", latitude=87.65, longitude=43.21)
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 100
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def image_upload_url(train_id):
    return reverse(
        "train_station_system:train-upload-image",
        args=[train_id]
    )


def detail_url(train_id):
    return reverse(
        "train_station_system:train-detail",
        args=[train_id]
    )


class TrainViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.train_type = TrainType.objects.create(name="Express")

    def test_create_train(self):
        """Test creating a new train"""
        url = TRAIN_URL
        payload = {
            "name": "New Train",
            "cargo_num": 100,
            "places_in_cargo": 50,
            "train_type": self.train_type.id,
        }

        result = self.client.post(url, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        train = Train.objects.get(id=result.data["id"])

        for key in payload:
            if key == "train_type":
                self.assertEqual(payload[key], train.train_type.id)
            else:
                self.assertEqual(payload[key], getattr(train, key))


class RouteViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        """Test creating a new route"""
        station_a = Station.objects.create(name="Station A", latitude=12.34, longitude=56.78)
        station_b = Station.objects.create(name="Station B", latitude=87.65, longitude=43.21)
        payload = {
            "source": station_a.id,
            "destination": station_b.id,
            "distance": 100,
        }
        url = reverse("train_station_system:route-list")
        result = self.client.post(url, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

        self.assertIn("id", result.data)

        route = Route.objects.get(id=result.data["id"])

        self.assertEqual(station_a.id, route.source.id)
        self.assertEqual(station_b.id, route.destination.id)
        self.assertEqual(payload["distance"], route.distance)

    def test_list_routes(self):
        """Test retrieving a list of routes"""
        station_a = Station.objects.create(name="Station A", latitude=12.34, longitude=56.78)
        station_b = Station.objects.create(name="Station B", latitude=87.65, longitude=43.21)
        sample_route(source=station_a, destination=station_b)
        result = self.client.get(reverse("train_station_system:route-list"))
        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

# class AuthenticatedJourneyApiTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             email="train@test.test",
#             password="difficult_password12345"
#         )
#         self.client.force_authenticate(self.user)
#
#
#         self.train_type = TrainType.objects.create(name="Freight")
#
#
#         self.station_a = Station.objects.create(name="Station A", latitude=0.0, longitude=0.0)
#         self.station_b = Station.objects.create(name="Station B", latitude=8.0, longitude=5.0)
#         self.station_c = Station.objects.create(name="Station C", latitude=4.5, longitude=11.0)
#         self.station_d = Station.objects.create(name="Station D", latitude=150.0, longitude=16.0)
#
#     def sample_train(self, **params):
#
#         defaults = {
#             "name": "Test Train",
#             "cargo_num": 100,
#             "places_in_cargo": 100,
#             "train_type": self.train_type
#         }
#         defaults.update(params)
#         return Train.objects.create(**defaults)
#
#     def test_filter_journeys_by_source(self):
#         """Test filtering journeys by source station"""
#         route_1 = Route.objects.create(source=self.station_a, destination=self.station_b, distance=100)
#         route_2 = Route.objects.create(source=self.station_c, destination=self.station_d, distance=150)
#
#
#         journey_1 = Journey.objects.create(
#             route=route_1,
#             train=self.sample_train(),
#             departure_time="2025-01-01T12:00:00Z",
#             arrival_time="2025-01-01T18:00:00Z"
#         )
#         journey_2 = Journey.objects.create(
#             route=route_2,
#             train=self.sample_train(),
#             departure_time="2025-01-01T12:00:00Z",
#             arrival_time="2025-01-01T18:00:00Z"
#         )
#
#
#         url = reverse("train_station_system:journey-list")
#         result = self.client.get(url, {"source__id": self.station_a.id})
#
#
#         print([journey['id'] for journey in result.data])
#
#         self.assertIn(journey_1.id, [journey['id'] for journey in result.data])
#         self.assertNotIn(journey_2.id, [journey['id'] for journey in result.data])
#
#     def test_filter_journeys_by_destination(self):
#         """Test filtering journeys by destination station"""
#         route_1 = Route.objects.create(source=self.station_a, destination=self.station_b, distance=100)
#         route_2 = Route.objects.create(source=self.station_c, destination=self.station_d, distance=150)
#
#
#         journey_1 = Journey.objects.create(
#             route=route_1,
#             train=self.sample_train(),
#             departure_time="2025-01-01T12:00:00Z",
#             arrival_time="2025-01-01T18:00:00Z"
#         )
#         journey_2 = Journey.objects.create(
#             route=route_2,
#             train=self.sample_train(),
#             departure_time="2025-01-01T12:00:00Z",
#             arrival_time="2025-01-01T18:00:00Z"
#         )
#
#
#         url = reverse("train_station_system:journey-list")
#         result = self.client.get(url, {"destination__id": self.station_b.id})
#
#         print([journey['id'] for journey in result.data])
#
#         self.assertIn(journey_1.id, [journey['id'] for journey in result.data])
#         self.assertNotIn(journey_2.id, [journey['id'] for journey in result.data])
