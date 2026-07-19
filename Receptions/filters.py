from django.db.models import Q
from django_filters import ChoiceFilter, CharFilter, FilterSet

from Account.models import Doctor
from Account.models import User
from Clinic.models import Clinics
from Receptions.models import Insurances, News


class UserFilter(FilterSet):
    role = ChoiceFilter(
        choices=[
            ("all", "همه"),
            ("supervisor", "سرپرست"),
            ("reception", "پذیرش"),
            ("patient", "بیمار"),
        ],
        method="filter_role",
    )

    q = CharFilter(method="filter_user_detail")

    class Meta:
        model = User
        fields = []

    def filter_role(self, queryset, name, value):
        if value == "all":
            return queryset.exclude(role="doctor")

        return queryset.filter(role=value)

    def filter_user_detail(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(username__icontains=value)
        )


class InsuranceFilter(FilterSet):
    q = CharFilter(method="filter_insurance_detail")

    class Meta:
        model = Insurances
        fields = []

    def filter_insurance_detail(self, queryset, name, value):
        return Insurances.objects.filter(name__icontains=value)


class ClinicFilter(FilterSet):
    q = CharFilter(method="filter_clinic_detail")

    class Meta:
        model = Clinics
        fields = []

    def filter_clinic_detail(self, queryset, name, value):
        return Clinics.objects.filter(name__icontains=value)


class ScheduleFilter(FilterSet):
    q = CharFilter(method="filter_doctor")

    class Meta:
        model = Doctor
        fields = []

    def filter_doctor(self, queryset, name, value):
        return (
            queryset.filter(user__schedules__status="Open")
            .filter(
                Q(user__first_name__icontains=value)
                | Q(user__last_name__icontains=value)
                | Q(clinic__name__icontains=value)
            )
            .distinct()
        )


class NewsFilter(FilterSet):
    q = CharFilter(method="filter_news")

    class Meta:
        model = News
        fields = []

    def filter_news(self, queryset, name, value):
        return News.objects.filter(Q(title__icontains=value) | Q(text__icontains=value))
