from django.contrib import admin

from Schedule.models import Schedule


# Register your models here.


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    date_hierarchy = "created_date"
    fields = ["doctor", "start_time", "end_time", "schedule_date", "status"]
    list_display = (
        "doctor",
        "start_time",
        "end_time",
        "schedule_date",
        "status",
        "created_date",
        "updated_date",
    )
    search_fields = ("doctor", "schedule_date")
