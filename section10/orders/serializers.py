from rest_framework import serializers

from .models import Customer, Order


class OrderSerializer(serializers.ModelSerializer[Order]):
    class Meta:
        model = Order
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer[Customer]):
    orders = OrderSerializer(read_only=True, many=True)

    class Meta:
        model = Customer
        fields = "__all__"
