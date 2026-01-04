from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Passenger
from .serializers import PassengerSerializer


@api_view(["GET", "POST"])
def passenger_list(request: Request) -> Response:
    match request.method:
        case "GET":
            passengers = Passenger.objects.all()
            serializer = PassengerSerializer(passengers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        case "POST":
            serializer = PassengerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        case _:
            return Response(
                {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )


@api_view(["GET", "PUT", "DELETE", "PATCH"])
def passenger_detail(request: Request, pk: int) -> Response:
    match request.method:
        case "GET":
            passenger = get_object_or_404(Passenger, pk=pk)
            serializer = PassengerSerializer(passenger)
            return Response(serializer.data, status=status.HTTP_200_OK)
        case "PUT":
            serializer = PassengerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        case "DELETE":
            passenger = get_object_or_404(Passenger, pk=pk)
            passenger.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        case "PATCH":
            passenger = get_object_or_404(Passenger, pk=pk)
            serializer = PassengerSerializer(passenger, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        case _:
            return Response(
                {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
