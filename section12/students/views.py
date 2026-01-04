from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from .models import Student
from .serializers import StudentSerializer


class StudentPagination(PageNumberPagination):
    page_size = 2


class StudentViewSet(ModelViewSet[Student]):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = StudentPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "score"]
    ordering_fields = ["name", "score"]
