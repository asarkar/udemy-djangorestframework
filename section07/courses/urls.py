from django.urls import path

from .views import CourseDetail, CourseList

urlpatterns = [
    path("courses/", CourseList.as_view(), name="course-list"),
    path("courses/<int:pk>/", CourseDetail.as_view(), name="course-detail"),
]
