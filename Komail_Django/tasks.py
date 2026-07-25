from celery import shared_task
from django.core.cache import cache
from utils.redis_cache import RedisCacheManager
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

    cache_manager = RedisCacheManager()
    cache_key = f"pending_reservations_count_{user_id}"

    if cache_manager.get(cache_key):
        cache_manager.delete(cache_key)
        cache_manager.set(cache_key, count, timeout=60)

    else:
        cache_manager.set(cache_key, count, timeout=60)

    return count


