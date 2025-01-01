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


class TrainImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@example.com", "difficult_password"
        )
        self.client.force_authenticate(self.user)
        self.train = sample_train()

    def tearDown(self):
        self.train.image.delete()

    def test_upload_image_to_train(self):
        url = image_upload_url(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            result = self.client.post(url, {"image": ntf}, format="multipart")
        self.train.refresh_from_db()
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertIn("image", result.data)
        self.assertTrue(os.path.exists(self.train.image.path))

    def test_upload_invalid_image(self):
        url = image_upload_url(self.train.id)
        result = self.client.post(url, {"image": "not image"}, format="multipart")
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_train_with_image(self):
        url = TRAIN_URL
        train_type = TrainType.objects.create(name="Freight")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            payload = {
                "name": "New Train",
                "cargo_num": 100,
                "places_in_cargo": 50,
                "train_type": train_type.id,
                "image": ntf,
            }
            result = self.client.post(url, payload, format="multipart")
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(id=result.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(train, key))
        self.assertTrue(os.path.exists(train.image.path))

    def test_image_url_is_shown_in_train_detail(self):
        """Test if the image URL is shown in the train detail view"""
        url = image_upload_url(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        result = self.client.get(detail_url(self.train.id))
        self.assertIn("image", result.data)


class TicketValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123"
        )
        self.client.force_authenticate(self.user)
        self.train = sample_train()
        self.route = sample_route()
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2024-04-02 10:00:00",
            arrival_time="2024-04-02 14:00:00"
        )

    def test_ticket_validation_valid(self):
        """Test valid ticket creation"""
        ticket = sample_ticket(cargo=50, seat=30, journey=self.journey, order=self.route)
        self.assertEqual(ticket.cargo, 50)
        self.assertEqual(ticket.seat, 30)

    def test_ticket_validation_invalid_cargo(self):
        """Test invalid cargo number"""
        with self.assertRaises(ValidationError):
            sample_ticket(cargo=150, seat=30, journey=self.journey, order=self.route)

    def test_ticket_validation_invalid_seat(self):
        """Test invalid seat number"""
        with self.assertRaises(ValidationError):
            sample_ticket(cargo=50, seat=600, journey=self.journey, order=self.route)


class TrainViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123"
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
            self.assertEqual(payload[key], getattr(train, key))


class RouteViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "password123"
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
        route = Route.objects.get(id=result.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(route, key))

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