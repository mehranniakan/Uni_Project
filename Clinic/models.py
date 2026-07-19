import uuid

from django.db import models


# Create your models here.


class Clinics(models.Model):
    TYPE_CHOICES = [
        ("normal", "عادی"),
        ("paraclinic", "پاراکلینیک"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="نام")
    type = models.CharField(
        max_length=20, default="normal", choices=TYPE_CHOICES, verbose_name="نوع"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clinic"
        verbose_name_plural = "Clinics"
        db_table = "Clinics"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["type"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "type"], name="unique_clinic_name_type"
            )
        ]

    def __str__(self):
        return self.name


class DoctorServices(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="نام خدمت")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        db_table = "Doctor_Service"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


# class Chat(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_id = models.ForeignKey(AdminUser, related_name='Users',on_delete=models.CASCADE)
#     doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#     admin_id = models.ForeignKey(AdminUser, related_name='Admins',on_delete=models.CASCADE)
#     autor = models.CharField(max_length=1)
#     status = models.BooleanField(default=True)
#     Created_Date = models.DateTimeField(auto_now_add=True)
#     Updated_Date = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         verbose_name = 'Chat'
#         verbose_name_plural = "Chats"
#         db_table = 'Chats'
#         ordering = ['-Created_Date']
#         indexes = [
#             models.Index(fields=['user_id']),
#             models.Index(fields=['doctor_id']),
#             models.Index(fields=['admin_id']),
#         ]
#
#     def __str__(self):
#         return f"{self.user_id} {self.doctor_id} {self.admin_id}"
