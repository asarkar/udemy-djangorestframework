import django_filters
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from .models import Flight


class FlightFilter(django_filters.FilterSet):
    origin = django_filters.CharFilter(lookup_expr="iexact")
    destination = django_filters.CharFilter(lookup_expr="iexact")
    departure_date = django_filters.DateFilter()

    class Meta:
        model = Flight
        fields = ["origin", "destination", "departure_date"]

    def filter_queryset(self, queryset: QuerySet[Flight]) -> QuerySet[Flight]:
        # `cleaned_data` gives validated, type-converted filter values - not raw query strings.
        data = self.form.cleaned_data
        required = ["origin", "destination", "departure_date"]
        provided = [field for field in required if data.get(field)]

        if provided and len(provided) < len(required):
            raise ValidationError(
                {"error": "origin, destination, and departure_date are all required"}
            )

        return super().filter_queryset(queryset)
