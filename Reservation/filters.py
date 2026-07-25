from django_filters.filters import CharFilter, ChoiceFilter
from django_filters.filterset import FilterSet
from django.db.models import Q

from Reservation.models import Reservation


class ReservationFilter(FilterSet):
    q = CharFilter(method="filter_reservation")

    status = ChoiceFilter(
        choices=[
            ('pending', 'در دست اقدام'),
            ('answered', 'انجام شده'),
            ('cancelled', 'کنسل شده'),
        ],
        method="filter_status",
    )

    class Meta:
        model = Reservation
        fields = []

    def filter_reservation(self, queryset, name, value):
        query = queryset.filter(
            Q(schedule__doctor__first_name__icontains=value)
            | Q(schedule__doctor__last_name__icontains=value)
            | Q(user__username__icontains=value)
            | Q(sub_user__national_id__icontains=value)
        )

        return query

    def filter_status(self, queryset, name, value):
        if value in ["pending", "answered", "cancelled"]:

            query = queryset.filter(status=value)

            return query
        else:
            return queryset.filter()
