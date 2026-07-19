from django.contrib import admin

from .models import Reservation


# Register your models here.


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_date"
    fields = [
        "user",
        "schedule",
        "reception",
        "type",
        "status",
    ]
    list_display = (
        "user_id",
        "schedule_id",
        "sub_user",
        "status",
        "doctor_info",
        "reception",
        "patient_info",
        "schedule_info",
        "type",
        "created_date",
        "updated_date",
    )
    search_fields = ("user", "schedule", "sub_user")

    def patient_info(self, obj):
        if obj.user:
            user = obj.user
            return f"{user.first_name} {user.last_name} ({user.username or user.mobile_number})"

    def doctor_info(self, obj):

        if obj.schedule and obj.schedule.doctor:
            doctor = obj.schedule.doctor
            return f" {doctor.first_name} {doctor.last_name}"

    def schedule_info(self, obj):
        if obj.schedule:
            schedule = obj.schedule
            return f"{schedule.schedule_date} {schedule.start_time}-{schedule.end_time}"
