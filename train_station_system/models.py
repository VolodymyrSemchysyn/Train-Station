from django.conf import settings
from django.db import models


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