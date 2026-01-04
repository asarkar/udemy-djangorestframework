from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
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
    permission_classes = [IsAuthenticated]


# --- Implementation using manual filtering kept for reference ---
#
# from rest_framework.request import Request
# from rest_framework.response import Response
# from rest_framework import status
#
# class FlightViewSet(ModelViewSet[Flight]):
#     queryset = Flight.objects.all()
#     serializer_class = FlightSerializer
#
#     def list(self, request: Request) -> Response:
#         source = request.query_params.get("source")
#         destination = request.query_params.get("destination")
#         departure_date = request.query_params.get("departure_date")
#
#         # If search params provided, filter; otherwise return all
#         if source and destination and departure_date:
#             flights = Flight.objects.filter(
#                 source__iexact=source,
#                 destination__iexact=destination,
#                 departure_date=departure_date,
#             )
#         elif source or destination or departure_date:
#             # Partial params = error
#             return Response(
#                 {"error": "source, destination, and departure_date are all required"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         else:
#             # No params = return all flights
#             flights = self.get_queryset()
#
#         serializer = self.get_serializer(flights, many=True)
#         return Response(serializer.data)


class PassengerViewSet(ModelViewSet[Passenger]):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer


class ReservationViewSet(ModelViewSet[Reservation]):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> type[BaseSerializer[Reservation]]:
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationSerializer
