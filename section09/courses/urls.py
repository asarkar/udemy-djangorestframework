from rest_framework.routers import DefaultRouter

from .views import CourseViewSet

router = DefaultRouter()
# With basename="course", the router generates these named URLs:
#   course-list -> for the list/create endpoint (/courses/)
#   course-detail -> for the retrieve/update/destroy endpoint (/courses/{pk}/)
router.register("courses", CourseViewSet, basename="course")

urlpatterns = router.urls
