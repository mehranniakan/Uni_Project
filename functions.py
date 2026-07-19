import uuid

from django.core import signing


def unsign_id(id):
    try:
        user_id = signing.loads(id)
        return uuid.UUID(user_id)
    except signing.BadSignature:
        return None
