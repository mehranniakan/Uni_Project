from django.urls import path

from Schedule.views import ScheduleListView

urlpatterns = [
    path("schedule", ScheduleListView.as_view(), name="schedule_pub"),
]
