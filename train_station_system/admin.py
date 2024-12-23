from django.contrib import admin

from train_station_system.models import (
    Station,
    Train,
    Crew,
    TrainType,
    Order,
    Ticket,
    Route,
    Journey
)

admin.site.register(Station)
admin.site.register(Crew)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(Route)
admin.site.register(Journey)
