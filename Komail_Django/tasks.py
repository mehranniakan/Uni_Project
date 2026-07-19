from celery import shared_task
from django.core.cache import cache

from Account.models import User
from Reservation.models import Reservation


@shared_task
def check_pending_reservations(user_id):
    user = User.objects.get(id=user_id)

    if user.role == "supervisor":
        count = Reservation.objects.filter(status="pending").count()

    elif user.role == "reception":
        clinics = user.reception.privileges.values_list("id", flat=True)

        count = Reservation.objects.filter(
            status="pending", schedule__doctor__doctor__clinic_id__in=clinics
        ).count()
    else:
        return 0

    cache_key = f"pending_reservations_count_{user_id}"
    cache.set(cache_key, count, timeout=None)

    return count
