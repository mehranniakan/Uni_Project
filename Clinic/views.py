import uuid

from django.db.models import F, Count
from django.http import Http404
from django.views.generic import ListView
from django.views.generic.base import TemplateView

from Account.models import Doctor, User
from Clinic.filter import DoctorFilter
from Clinic.models import Clinics
from Schedule.models import Schedule
from functions import unsign_id


# Create your views here.
class DoctorDetailView(TemplateView):
    template_name = "main/doctor_detail.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        doc_id = self.request.GET.get("doc_id")
        sch_id = self.request.GET.get("sch_id")

        if doc_id:
            doc_name = self.request.GET.get("doc_name")
            doc_last = self.request.GET.get("doc_last")
            doc_spec = self.request.GET.get("spec")
            doc_super_spec = self.request.GET.get("sup_spec")
            clinic = self.request.GET.get("sec")
            pic = self.request.GET.get("pic")

            schedule = Schedule.objects.filter(
                status="Open",
                doctor__doctor__id=uuid.UUID(doc_id),  # اگر Schedule به doctor متصل است
            ).first()

            if schedule:
                # اگر Schedule وجود دارد، ظرفیت باقیمانده را محاسبه کن
                cap = (
                    Schedule.objects.filter(
                        status="Open",
                    )
                    .annotate(
                        free_pt_cap=F("doctor__doctor__pt_cap") - Count("reservations")
                    )
                    .values_list("free_pt_cap", flat=True)
                    .first()
                )

                cap = cap if cap is not None else 0
            else:
                doctor = Doctor.objects.get(user__id=uuid.UUID(doc_id))
                cap = doctor.pt_cap

            context["doc_id"] = doc_id
            context["doc_name"] = doc_name
            context["doc_last"] = doc_last
            context["spec"] = doc_spec
            context["sup_spec"] = doc_super_spec
            context["clinic"] = clinic
            context["pic"] = pic
            context["cap"] = cap

        elif sch_id:
            doc_name = self.request.GET.get("doc_name")
            doc_last = self.request.GET.get("doc_last")
            doc_spec = self.request.GET.get("spec")
            doc_super_spec = self.request.GET.get("sup_spec")
            clinic = self.request.GET.get("sec")
            pic = self.request.GET.get("pic")
            services = self.request.GET.get("serv")
            start = self.request.GET.get("start")
            end = self.request.GET.get("end")

            context["sch_id"] = sch_id
            context["doc_name"] = doc_name
            context["doc_last"] = doc_last
            context["doc_spec"] = doc_spec
            context["sup_spec"] = doc_super_spec
            context["clinic"] = clinic
            context["pic"] = pic
            context["service"] = services
            context["start"] = start
            context["end"] = end

        else:
            raise Http404()

        return context


class DoctorListView(ListView):
    model = User
    template_name = "main/doctors_pub.html"
    http_method_names = ["get"]
    context_object_name = "doctors"
    paginate_by = 15
    filterset_class = DoctorFilter

    def get_queryset(self):

        self.clinic_id = unsign_id(self.request.GET.get("id"))

        if not self.clinic_id:
            raise Http404()

        # Main Query
        qs = (
            User.objects.filter(
                role="doctor",
                is_active=True,
                doctor__clinic=self.clinic_id,
                doctor__status="Active",
            )
            .select_related("doctor", "doctor__clinic")
            .prefetch_related("doctor__services")
        )

        print(qs.count())

        self.filterset = self.filterset_class(self.request.GET, queryset=qs)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["filter"] = self.filterset

        if self.clinic_id:
            ctx["clinics"] = Clinics.objects.filter(id=self.clinic_id)
        else:
            ctx["clinics"] = Clinics.objects.all()

        return ctx
