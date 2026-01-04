from rest_framework import serializers

from .models import Passenger


class PassengerSerializer(serializers.ModelSerializer[Passenger]):
    class Meta:
        model = Passenger
        fields = "__all__"
