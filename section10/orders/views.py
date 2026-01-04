from rest_framework.viewsets import ModelViewSet

from .models import Customer, Order
from .serializers import CustomerSerializer, OrderSerializer


class CustomerViewSet(ModelViewSet[Customer]):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class OrderViewSet(ModelViewSet[Order]):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
