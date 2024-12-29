# Generated by Django 5.1.4 on 2024-12-29 21:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("train_station_system", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="journey",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="journeys",
                to="train_station_system.route",
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="destination",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="routes_destination",
                to="train_station_system.station",
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="routes_source",
                to="train_station_system.station",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="journey",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="train_station_system.journey",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="train_station_system.order",
            ),
        ),
        migrations.AddField(
            model_name="journey",
            name="train",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="journeys",
                to="train_station_system.train",
            ),
        ),
        migrations.AddField(
            model_name="train",
            name="train_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="trains",
                to="train_station_system.traintype",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("cargo", "seat", "journey")},
        ),
    ]