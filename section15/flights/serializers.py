from typing import Any

from rest_framework import serializers

from .models import Flight, Passenger, Reservation


class FlightSerializer(serializers.ModelSerializer[Flight]):
    class Meta:
        model = Flight
        fields = "__all__"

    def validate_flight_number(self, value: str) -> str:
        if not value.isascii() or not value.isalnum():
            raise serializers.ValidationError(
                "Flight number must contain only alphanumeric ASCII characters"
            )
        return value


class PassengerSerializer(serializers.ModelSerializer[Passenger]):
    class Meta:
        model = Passenger
        fields = "__all__"
        read_only_fields = ["id"]


class ReservationSerializer(serializers.ModelSerializer[Reservation]):
    class Meta:
        model = Reservation
        fields = "__all__"


class ReservationCreateSerializer(serializers.Serializer[Reservation]):
    flight_id = serializers.IntegerField()
    passenger = PassengerSerializer()

    def validate_flight_id(self, value: int) -> int:
        if not Flight.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Flight not found")
        return value

    def create(self, validated_data: dict[str, Any]) -> Reservation:
        flight = Flight.objects.get(pk=validated_data["flight_id"])
        passenger_data = validated_data["passenger"]

        passenger, _ = Passenger.objects.get_or_create(
            email=passenger_data["email"],
            defaults=passenger_data,
        )

        return Reservation.objects.create(flight=flight, passenger=passenger)
