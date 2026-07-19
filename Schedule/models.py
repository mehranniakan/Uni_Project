import uuid

from django.db import models

from Account.models import User


# Create your models here.


class Schedule(models.Model):
    STATUS_CHOICES = [
        ("Cancelled", "کنسل شده"),
        ("Closed", "به اتمام رسیده"),
        ("Open", "جاری"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedules")
    start_time = models.TimeField()
    end_time = models.TimeField()
    schedule_date = models.DateField()
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default="Open")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        db_table = "Schedule"
        ordering = ["-schedule_date", "start_time"]
        indexes = [
            models.Index(fields=["doctor", "schedule_date", "status"]),
        ]

    def __str__(self):
        return (
            f"{self.doctor.first_name} {self.doctor.last_name} - {self.schedule_date}"
        )
