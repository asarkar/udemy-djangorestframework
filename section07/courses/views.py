from typing import Any

from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Course
from .serializers import CourseSerializer


class CourseList(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericAPIView[Course],
):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:
        return self.list(request, *args, **kwargs)

    def post(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:
        return self.create(request, *args, **kwargs)


class CourseDetail(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericAPIView[Course],
):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:
        return self.retrieve(request, *args, **kwargs)

    def put(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:
        return self.update(request, *args, **kwargs)

    def patch(self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Response:
        return self.partial_update(request, *args, **kwargs)

    def delete(
        self, request: Request, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> Response:
        return self.destroy(request, *args, **kwargs)
