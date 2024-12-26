from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError


class Crew(models.Model):
    first_name = models.CharField(max_length=55)
    last_name = models.CharField(max_length=55)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Train(models.Model):
    name = models.CharField(max_length=55)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        "TrainType",
        on_delete=models.CASCADE,
        related_name="trains"
    )

    def __str__(self):
        return f"{self.name} {self.cargo_num}"

    @property
    def number_of_seats(self):
        return self.cargo_num * self.places_in_cargo


class TrainType(models.Model):
    name = models.CharField(max_length=55)

    def __str__(self):
        return f"{self.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.created_at}"


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        "Journey",
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    def __str__(self):
        return (f"{self.cargo}, {self.seat}, "
                f"{self.journey} {self.order}")

    @staticmethod
    def validate_ticket(cargo, seat, train, error_to_raise=ValidationError):
        if not (1 <= cargo <= train.cargo_num):
            raise error_to_raise(
                {"cargo": f"Cargo number must be between 1 and {train.cargo_num}."}
            )
        if not (1 <= seat <= train.number_of_seats):
            raise error_to_raise(
                {"seat": f"Seat number must be between 1 and {train.number_of_seats}."}
            )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        unique_together = ("cargo", "seat", "journey")


class Station(models.Model):
    name = models.CharField(max_length=55)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name}"


class Route(models.Model):
    source = models.ForeignKey(
        "Station",
        on_delete=models.CASCADE,
        related_name="routes"
    )
    destination = models.ForeignKey(
        "Station",
        on_delete=models.CASCADE,
        related_name="routes"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source} -> {self.destination}, {self.distance}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def __str__(self):
        return f"{self.train}, {self.departure_time}, {self.arrival_time}"
