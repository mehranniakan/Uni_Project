import uuid

from django.db import models

from Account.models import User, SubUser
from Schedule.models import Schedule


# Create your models here.


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("cancelled", "کنسل شده"),
        ("pending", "در انتظار پاسخ"),
        ("answered", "پاسخ داده شد"),
    ]

    TYPE_CHOICES = [
        ("chat", "مشاوره متنی"),
        ("online_reservation", "رزرو نوبت آنلاین"),
        ("oncall_reservation", "رزرو نوبت تلفنی"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations"
    )

    sub_user = models.ForeignKey(
        SubUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="reservations",
    )

    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name="reservations"
    )

    type = models.CharField(
        max_length=25, default="online_reservation", choices=TYPE_CHOICES
    )

    reception = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
        related_name="received_reservations",
    )

    status = models.CharField(max_length=18, default="pending", choices=STATUS_CHOICES)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        db_table = "Reservation"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["schedule", "status"]),
            models.Index(fields=["reception"]),
        ]

    def __str__(self):
        return str(self.id)
