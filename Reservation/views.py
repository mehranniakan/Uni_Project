import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from Account.models import SubUser
from Reservation.filters import ReservationFilter
from Reservation.models import Reservation
from Schedule.models import Schedule


def user_only(user):
    return user.is_authenticated and user.is_active and user.role == "patient"


def reception_only(user):
    return user.is_authenticated and user.role == "reception" and user.is_active


def supervisor_only(user):
    return user.is_authenticated and user.role == "supervisor" and user.is_active


def supervisor_or_reception(user):
    return supervisor_only(user) or reception_only(user)


@method_decorator(user_passes_test(supervisor_or_reception), name="dispatch")
class ReservationAdminListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "receptions & users/reservation_list_admin.html"
    filterset_class = ReservationFilter
    paginate_by = 15
    context_object_name = "reservations"
    http_method_names = ["get"]

    def get_queryset(self):
        if self.request.user.role == "supervisor":
            reservations = Reservation.objects.select_related(
                "schedule",
                "schedule__doctor",
                "schedule__doctor__doctor",
                "schedule__doctor__doctor__clinic",
                "user",
                "sub_user",
                "user__patient",
                "reception",
            )

        else:
            reservations = Reservation.objects.filter(
                schedule__doctor__doctor__clinic__in=self.request.user.reception.privileges.all()
            ).select_related(
                "schedule",
                "schedule__doctor",
                "schedule__doctor__doctor",
                "schedule__doctor__doctor__clinic",
                "user",
                "sub_user",
                "patient",
                "reception",
            )

        filter_set = self.filterset_class(
            self.request.GET,
            queryset=reservations,
        )
        return filter_set.qs


@method_decorator(user_passes_test(user_only), name="dispatch")
class ReservationUserListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "receptions & users/reservation_list.html"
    http_method_names = ["get"]
    paginate_by = 15
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.select_related(
            "schedule",
            "schedule__doctor",
            "schedule__doctor__doctor__clinic",
            "schedule__doctor__doctor",
            "sub_user",
        ).filter(
            user_id=self.request.user.id,
            status__in=["pending", "answered"],
            schedule__status="Open",
        )


@login_required
def set_reservation(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data = json.loads(request.body)
    sch_id = data.get("sch_id")
    sub_id = data.get("sub_id")

    if not sch_id:
        return JsonResponse(
            {"status": "error", "message": "برنامه ای با این شناسه یافت نشد !"},
            status=404,
        )

    try:
        with transaction.atomic():
            schedule = (
                Schedule.objects.select_for_update()
                .select_related("doctor", "doctor__doctor")
                .filter(id=sch_id, status="Open")
                .first()
            )

            if not schedule:
                return JsonResponse(
                    {"status": "error", "message": "برنامه ای با این شناسه یافت نشد !"},
                    status=404,
                )

            doctor_profile = getattr(schedule.doctor, "doctor", None)

            if not doctor_profile:
                return JsonResponse(
                    {"status": "error", "message": "اطلاعات پزشک یافت نشد !"},
                    status=404,
                )

            # بررسی ظرفیت
            current_count = Reservation.objects.filter(schedule=schedule).count()

            if current_count >= doctor_profile.pt_cap:
                return JsonResponse(
                    {"status": "error", "message": "ظرفیت نوبت دهی به اتمام رسید !"},
                    status=400,
                )

            # بررسی تعداد رزرو در یک روز
            daily_count = Reservation.objects.filter(
                user=request.user, schedule__schedule_date=schedule.schedule_date
            ).count()

            if daily_count >= 10:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "حداکثر تعداد نوبت قابل دریافت در یک روز 10 عدد می باشد !",
                    },
                    status=400,
                )

            sub_user = None

            if sub_id:
                patient = getattr(request.user, "patient", None)

                if not patient:
                    return JsonResponse(
                        {"status": "error", "message": "اطلاعات بیمار یافت نشد !"},
                        status=404,
                    )

                sub_user = SubUser.objects.filter(id=sub_id, user=patient).first()

                if not sub_user:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": "فرد تحت تکفلی با این شناسه یافت نشد !",
                        },
                        status=404,
                    )

            # بررسی رزرو تکراری
            duplicate = Reservation.objects.filter(
                schedule=schedule, user=request.user, sub_user=sub_user
            ).exists()

            if duplicate:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "شما قبلا برای این پزشک نوبت گرفته اید !",
                    },
                    status=400,
                )

            Reservation.objects.create(
                user=request.user,
                sub_user=sub_user,
                schedule=schedule,
                type="online_reservation",
                status="pending",
            )

            messages.success(request, "نوبت شما با موفقیت رزرو شد!")

            return JsonResponse(
                {"status": "success", "message": "رزرو با موفقیت انجام شد."}
            )

    except Exception as e:
        print(e)
        return JsonResponse(
            {"status": "error", "message": "خطای سروری رخ داد."}, status=500
        )


@login_required
@user_passes_test(supervisor_or_reception)
def reservation_apply(request):
    if request.method == "POST":
        if request.POST.get("pk"):
            reservation = get_object_or_404(Reservation, pk=request.POST.get("pk"))
            reservation.status = "answered"
            reservation.reception = request.user
            reservation.save()
            messages.success(request, "نوبت مورد نظر با موفقیت تکمیل شد !")

            return redirect("reservation_list_admin")
        else:
            return redirect("index.html")
    else:
        return redirect("index.html")
