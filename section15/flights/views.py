from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet

from .filters import FlightFilter
from .models import Flight, Passenger, Reservation
from .serializers import (
    FlightSerializer,
    PassengerSerializer,
    ReservationCreateSerializer,
    ReservationSerializer,
)


class FlightViewSet(ModelViewSet[Flight]):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FlightFilter


class PassengerViewSet(ModelViewSet[Passenger]):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer


class ReservationViewSet(ModelViewSet[Reservation]):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_serializer_class(self) -> type[BaseSerializer[Reservation]]:
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer
