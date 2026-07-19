from django.core.cache import cache


def reservations_count(request):
    return {
        "pending_reservations_count": cache.get(
            f"pending_reservations_count_{request.user.id}", 0
        )
    }
