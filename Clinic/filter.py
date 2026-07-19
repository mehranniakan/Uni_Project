import django_filters
from django.db.models import Q

from Account.models import User


class DoctorFilter(django_filters.FilterSet):
    doctor_name = django_filters.CharFilter(
        method="filter_doctor_name", label="نام پزشک"
    )

    doctor_sex = django_filters.ChoiceFilter(
        field_name="sex",
        choices=[("Male", "مرد"), ("Female", "زن")],
        label="جنسیت پزشک",
    )

    doctor_speciality = django_filters.CharFilter(
        method="filter_doctor_spec", label="تخصص یا فوق تخصص"
    )

    doctor_clinic = django_filters.UUIDFilter(
        field_name="doctor__clinic", lookup_expr="exact", label="کلینیک"
    )

    class Meta:
        model = User
        fields = []

    def filter_doctor_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value)
        )

    def filter_doctor_spec(self, queryset, name, value):
        return queryset.filter(
            Q(doctor__speciality__icontains=value)
            | Q(doctor__super_speciality__icontains=value)
        )
