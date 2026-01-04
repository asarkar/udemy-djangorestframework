from rest_framework.viewsets import ModelViewSet

from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(ModelViewSet[Course]):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
