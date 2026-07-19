from django import template
from django.core import signing

register = template.Library()


@register.filter
def sign(value):
    return signing.dumps(str(value))


@register.filter
def unsign(value):
    try:
        return signing.loads(value)
    except signing.BadSignature:
        return None
