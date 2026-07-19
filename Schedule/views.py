from django.views.generic import ListView
from Clinic.models import Clinics
from Schedule.filter import ScheduleFilter
from Schedule.models import Schedule


# Create your views here.


class ScheduleListView(ListView):
    model = Schedule
    template_name = "schedule_list.html"
    context_object_name = "schedules"
    paginate_by = 15

    def get_queryset(self):
        # Base Queryset → همیشه کل برنامه را نشان می‌دهد
        qs = (
            Schedule.objects.select_related("doctor", "doctor__doctor__clinic")
            .filter(status="Open")
            .order_by("-start_time")
        )

        # FilterSet را روی QS اعمال می‌کنیم
        self.filterset = ScheduleFilter(self.request.GET, queryset=qs)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filterset"] = self.filterset  # فرم فیلتر
        ctx["clinics"] = Clinics.objects.all()

        print("تعداد schedules در context:", len(ctx["schedules"]))
        return ctx
