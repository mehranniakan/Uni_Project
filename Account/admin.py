from django.contrib import admin

from Account.models import Doctor, Patient, User, Reception, Supervisor, SubUser


@admin.register(User)
class User(admin.ModelAdmin):
    fields = [
        "first_name",
        "last_name",
        "username",
        "birthdate",
        "mobile_number",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    list_display = (
        "first_name",
        "last_name",
        "username",
        "mobile_number",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_date",
        "updated_date",
    )
    search_fields = ("username", "last_name")


@admin.register(Doctor)
class DoctorsAdmin(admin.ModelAdmin):
    fields = [
        "speciality",
        "services",
        "super_speciality",
        "clinic",
        "pic",
        "description",
        "status",
        "pt_cap",
        "is_popular",
        "is_top",
    ]
    list_display = (
        "get_name",
        "clinic",
        "speciality",
        "super_speciality",
        "status",
        "pt_cap",
        "pic",
        "is_popular",
        "is_top",
    )

    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    fields = [
        "user",
        "insurance_base",
        "insurance_supp",
        "insurance_full",
        "address",
        "status",
    ]
    list_display = (
        "get_name",
        "get_username",
        "insurance_base",
        "insurance_supp",
        "insurance_full",
        "address",
    )

    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    def get_username(self, obj):
        return obj.user.username


@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    fields = ["user", "privileges", "status"]
    list_display = ("get_name", "get_username", "get_sex")

    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    def get_username(self, obj):
        return obj.user.username

    def get_sex(self, obj):
        return obj.user.sex


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ("get_name", "get_username", "get_sex")

    def get_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    def get_username(self, obj):
        return obj.user.username

    def get_sex(self, obj):
        return obj.user.sex


@admin.register(SubUser)
class SubUsersAdmin(admin.ModelAdmin):
    date_hierarchy = "created_date"
    fields = ["first_name", "last_name", "relation", "birthdate"]
    list_display = (
        "first_name",
        "last_name",
        "relation",
        "birthdate",
        "created_date",
        "updated_date",
    )
    search_fields = ("first_name", "last_name")
