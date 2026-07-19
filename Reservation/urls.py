from django.urls import path

from Reservation.views import (
    ReservationUserListView,
    ReservationAdminListView,
    reservation_apply,
    set_reservation,
)

urlpatterns = [
    path(
        "reservation/list/",
        ReservationUserListView.as_view(),
        name="reservation_list_user",
    ),
    path(
        "reservation/list_admin/",
        ReservationAdminListView.as_view(),
        name="reservation_list_admin",
    ),
    path("reservation/list_admin/apply", reservation_apply, name="reservation_apply"),
    path("reservation/Set/", set_reservation, name="set_reservation"),
]
