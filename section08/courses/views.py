from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from .models import Course
from .serializers import CourseSerializer


class CourseList(ListCreateAPIView[Course]):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseDetail(RetrieveUpdateDestroyAPIView[Course]):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
