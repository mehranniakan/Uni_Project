from django.urls import path

from Clinic.views import DoctorDetailView, DoctorListView

urlpatterns = [
    path("doctor/detail/", DoctorDetailView.as_view(), name="doctor_detail"),
    path("doctor/list/by_cat/", DoctorListView.as_view(), name="doctor_list_pub"),
]
