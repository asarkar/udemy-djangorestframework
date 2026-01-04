from rest_framework.routers import DefaultRouter

from .views import FlightViewSet, PassengerViewSet, ReservationViewSet

router = DefaultRouter()
router.register("flights", FlightViewSet, basename="flight")
router.register("passengers", PassengerViewSet, basename="passenger")
router.register("reservations", ReservationViewSet, basename="reservation")

urlpatterns = router.urls
