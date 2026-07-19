from django.contrib import admin

from Receptions.models import Insurances, News


# Register your models here.
@admin.register(Insurances)
class InsurancesAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "created_date", "updated_date")
    list_filter = ("name", "type", "status")
    search_fields = ("name",)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "text", "created_date", "updated_date")
    list_filter = ("title",)
    search_fields = ("title",)
