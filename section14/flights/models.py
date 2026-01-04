from django.db import models


class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    airline = models.CharField(max_length=20)
    origin = models.CharField(max_length=20)
    destination = models.CharField(max_length=20)
    departure_date = models.DateField()
    departure_time = models.TimeField()


class Passenger(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    middle_name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=20)


class Reservation(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger = models.OneToOneField(Passenger, on_delete=models.CASCADE)
