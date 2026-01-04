from typing import Any

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


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


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(
    sender: type[AbstractBaseUser],
    instance: AbstractBaseUser | None = None,
    created: bool = False,
    **kwargs: dict[str, Any],
) -> None:
    if created and instance is not None:
        # `Token.objects.create()` expects `User` but we have `AbstractBaseUser`
        # (they're compatible at runtime, just not in the stubs).
        Token.objects.create(user=instance)  # type: ignore[misc]
