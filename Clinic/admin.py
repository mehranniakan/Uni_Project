from django.contrib import admin

from Clinic.models import Clinics, DoctorServices


# Register your models here.


@admin.register(Clinics)
class ClinicsAdmin(admin.ModelAdmin):
    date_hierarchy = "created_date"
    fields = ["name", "type"]
    list_display = ("name", "type", "created_date", "updated_date")
    search_fields = ("name", "type")
    sortable_by = ("-created_date",)


@admin.register(DoctorServices)
class DoctorServiceAdmin(admin.ModelAdmin):
    date_hierarchy = "created_date"
    fields = ["name"]
    list_display = ("name", "created_date", "updated_date")
    search_fields = ("name",)
    ordering = ("-created_date",)
    sortable_by = ("name", "created_date", "updated_date")

# @admin.register(Chat)
# class Chats(admin.ModelAdmin):
#     date_hierarchy = "Created_Date"
#     fields = ["doctor_id"]
#     list_display = ('doctor_id',)
#     search_fields = ('doctor_id',)
#     sortable_by = ('-Created_Date',)
