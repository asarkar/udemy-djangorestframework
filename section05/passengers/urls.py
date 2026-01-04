from django.urls import path

from . import views

urlpatterns = [
    path("passengers/", views.passenger_list, name="passenger-list"),
    path("passengers/<int:pk>/", views.passenger_detail, name="passenger-detail"),
]
