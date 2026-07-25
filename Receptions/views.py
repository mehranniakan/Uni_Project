import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.signing import BadSignature, loads
from django.db import transaction
from django.db.models import Prefetch
from django.db.models import Q, Count, F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.views.generic.base import TemplateView

from Account.models import SubUser, Doctor, User
from Clinic.models import Clinics
from Komail_Django.tasks import check_pending_reservations
from Receptions.filters import (
    UserFilter,
    InsuranceFilter,
    ClinicFilter,
    ScheduleFilter,
    NewsFilter,
)
from Receptions.forms import (
    DoctorForm,
    ScheduleForm,
    ClinicForm,
    InsuranceForm,
    EditUsersForm,
    NewsForm,
)

from Receptions.models import Insurances, News
from Reservation.models import Reservation
from Schedule.models import Schedule


# Create your views here.


def reception_only(user):
    return user.is_authenticated and user.role == "reception" and user.is_active


def supervisor_only(user):
    return user.is_authenticated and user.role == "supervisor" and user.is_active


def reception_or_supervisor_only(user):
    return supervisor_only(user) or reception_only(user)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "receptions & users/base_admin_panel.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        check_pending_reservations(request.user.id) 
        return super().get(request, *args, **kwargs)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class DoctorListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "receptions & users/doctor-list.html"
    paginate_by = 15
    http_method_names = ["get"]
    context_object_name = "doctors"

    search_value = None
    search_mode = False

    def get_queryset(self):
        if self.request.GET.get("q") and self.request.GET.get("page"):
            self.search_value = self.request.GET.get("q", "")
            self.docs = User.objects.filter(
                Q(first_name__icontains=self.search_value)
                | Q(last_name__icontains=self.search_value),
                role="doctor",
            ).select_related("doctor")
            return self.docs
        else:
            self.docs = User.objects.filter(role="doctor").select_related("doctor")
            return self.docs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("q") and self.request.GET.get("page"):
            context["search_value"] = self.search_value
            context["search_mode"] = True

        else:
            context["search_value"] = self.search_value
            context["search_mode"] = False

        return context


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class DoctorCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = DoctorForm
    template_name = "receptions & users/add&edit-doctor.html"
    success_url = reverse_lazy("doctor-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Action"] = "Add"
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["Action"] = "Add"
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "پزشک مورد نظر با موفقیت اضافه شد !")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = DoctorForm
    template_name = "receptions & users/add&edit-doctor.html"
    success_url = reverse_lazy("doctor-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Action"] = "Edit"
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["Action"] = "Edit"
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات پزشک مورد نظر با موفقیت اصلاح شد !")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "receptions & users/user & admin list.html"
    filterset_class = UserFilter
    context_object_name = "users"
    paginate_by = 15

    search_mode = False

    def get_queryset(self):

        self.role_count = []

        for key, value in User.ROLE_CHOICES:
            get_role_count = User.objects.filter(role=key).count()
            if key == "doctor":
                pass
            else:
                self.role_count.append(
                    {
                        "label": value,
                        "key": key,
                        "count": get_role_count,
                    }
                )

        queryset = User.objects.exclude(role="doctor").order_by("last_name")

        self.user_filter = self.filterset_class(self.request.GET, queryset=queryset)

        return self.user_filter.qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["roles"] = self.role_count
        context["filter"] = self.user_filter
        context["search_mode"] = self.search_mode
        context["current_role"] = self.request.GET.get("role", "all")

        return context


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditUsersForm
    template_name = "receptions & users/edit_user_admin.html"
    success_url = reverse_lazy("user_list")

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات کاربر مورد نظر با موفقیت اصلاح شد ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class InsuranceListView(LoginRequiredMixin, ListView):
    model = Insurances
    template_name = "receptions & users/insurence_list.html"
    filterset_class = InsuranceFilter
    context_object_name = "insurances"
    paginate_by = 15
    queryset = Insurances.objects.all()

    def get_queryset(self):
        filter_set = self.filterset_class(self.request.GET, queryset=self.queryset)
        return filter_set.qs


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class InsuranceCreateView(LoginRequiredMixin, CreateView):
    model = Insurances
    form_class = InsuranceForm
    template_name = "receptions & users/add&Edit_insurance.html"
    success_url = reverse_lazy("insurance_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Add"
        return context

    def form_valid(self, form):
        messages.success(self.request, "بیمه مورد نظر با موفقیت ثبت شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class InsuranceUpdateView(LoginRequiredMixin, UpdateView):
    model = Insurances
    form_class = InsuranceForm
    template_name = "receptions & users/add&Edit_insurance.html"
    success_url = reverse_lazy("insurance_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context

    def form_valid(self, form):
        messages.success(self.request, "بیمه مورد نظر با موفقیت اصلاح شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class ClinicListView(LoginRequiredMixin, ListView):
    model = Clinics
    template_name = "receptions & users/clinic_list.html"
    paginate_by = 15
    http_method_names = ["get"]
    filterset_class = ClinicFilter
    context_object_name = "clinics"

    def get_queryset(self):
        queryset = Clinics.objects.filter()
        filter_set = self.filterset_class(self.request.GET, queryset=queryset)
        return filter_set.qs


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class ClinicCreateView(LoginRequiredMixin, CreateView):
    model = Clinics
    form_class = ClinicForm
    template_name = "receptions & users/add&edit_clinic.html"
    success_url = reverse_lazy("clinic_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Add"
        return context

    def form_valid(self, form):
        messages.success(self.request, "کلینیک مورد نظر با موفقیت ثبت شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class ClinicUpdateView(LoginRequiredMixin, UpdateView):
    model = Clinics
    form_class = ClinicForm
    template_name = "receptions & users/add&edit_clinic.html"
    success_url = reverse_lazy("clinic_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context

    def form_valid(self, form):
        messages.success(self.request, "کلینیک مورد نظر با موفقیت اصلاح شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class ScheduleListView(LoginRequiredMixin, ListView):
    model = Schedule
    template_name = "receptions & users/schedule_account.html"
    paginate_by = 15
    filterset_class = ScheduleFilter
    http_method_names = ["get"]
    context_object_name = "schedules"

    def get_queryset(self):
        open_schedules = Schedule.objects.filter(status="Open").annotate(
            free_pt_cap=F("doctor__doctor__pt_cap") - Count("reservations")
        )

        doctors = (
            Doctor.objects.filter(user__schedules__status="Open")
            .select_related("user", "clinic")
            .prefetch_related(
                Prefetch(
                    "user__schedules", queryset=open_schedules, to_attr="open_schedules"
                )
            )
            .distinct()
        )

        filter_set = self.filterset_class(
            self.request.GET,
            queryset=doctors,
        )

        self.clinics = (
            Clinics.objects.filter(doctors__in=filter_set.qs)
            .distinct()
            .prefetch_related(Prefetch("doctors", queryset=doctors))
        )

        if self.request.user.role == "patient":
            self.subs = SubUser.objects.filter(user=self.request.user.patient)

        return self.clinics

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == "patient":
            context["subs"] = self.subs

        return context


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "receptions & users/add&edit_schedule.html"
    success_url = reverse_lazy("add-schedule")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"].title = "افزودن برنامه جدید"
        context["view"].is_update = False
        return context

    def form_valid(self, form):
        messages.success(self.request, "برنامه با موفقیت ثبت شد ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class ScheduleUpdateView(LoginRequiredMixin, UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = "receptions & users/add&edit_schedule.html"
    success_url = reverse_lazy("schedule")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"].title = "ویرایش برنامه"
        context["view"].is_update = True
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop("schedule_date")
        return form

    def form_valid(self, form):
        messages.success(self.request, "برنامه با موفقیت اصلاح شد ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@login_required
@user_passes_test(supervisor_only)
def close_schedule(request):
    if request.method == "GET":
        if Schedule.objects.filter(status="Open").exists():
            try:
                Schedule.objects.filter(status="Open").update(status="Closed")

                messages.success(request, "برنامه با موفقیت بسته شد !")
                return render(request, "schedule_account.html")
            except Exception:
                messages.error(request, "خطایی رخ داده لطفا مجددا تلاش کنید")
                return render(request, "schedule_account.html")
        else:
            messages.error(request, "برنامه ای برای بستن وجود ندارد !")
            return render(request, "schedule_account.html")

    else:
        return render(request, "index.html")


@login_required
@user_passes_test(supervisor_only)
def cancel_schedule(request):
    if request.method == "POST":
        if request.POST.get("pk"):
            try:
                real_uuid = loads(request.POST["pk"])
                real_uuid = uuid.UUID(real_uuid)
            except BadSignature:
                return redirect("main")

            check_id = Schedule.objects.filter(id=real_uuid, status="Open").first()

            if check_id:
                with transaction.atomic():
                    check_id.status = "Cancelled"
                    check_id.save()

                    Reservation.objects.filter(schedule__id=check_id.id).update(
                        status="cancelled", reception=request.user
                    )

                    check_pending_reservations.delay(request.user.id)

                    messages.success(request, "برنامه مورد نظر با موفقیت کنسل شد !")
                    return redirect("schedule")
            else:
                return redirect("main")
        else:
            return redirect("main")
    else:
        return redirect("main")


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class NewsListView(LoginRequiredMixin, ListView):
    model = News
    template_name = "receptions & users/news_list.html"
    paginate_by = 15
    filterset_class = NewsFilter
    http_method_names = ["get"]

    def get_queryset(self):
        filter_set = self.filterset_class(self.request.GET, queryset=News.objects.all())
        return filter_set.qs


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class NewsCreateView(LoginRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = "receptions & users/add&edit_news.html"
    success_url = reverse_lazy("news_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Add"
        return context

    def form_valid(self, form):
        messages.success(self.request, "خبر مورد نظر با موفقیت ثبت شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class NewsUpdateView(LoginRequiredMixin, UpdateView):
    model = News
    form_class = NewsForm
    template_name = "receptions & users/add&edit_news.html"
    success_url = reverse_lazy("news_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Add"
        return context

    def form_valid(self, form):
        messages.success(self.request, "خبر مورد نظر با موفقیت اصلاح شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(user_passes_test(supervisor_only), name="dispatch")
class NewsDeleteView(DeleteView):
    model = News
    success_url = reverse_lazy("news_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "خبر مورد نظر با موفقیت حذف شد")
        return super().delete(request, *args, **kwargs)
