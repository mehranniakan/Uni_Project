import uuid

from django.core.validators import FileExtensionValidator
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class Insurances(models.Model):
    TYPE_CHOICES = [
        ("Base", "بیمه پایه"),
        ("Supplementary", "بیمه تکمیلی"),
        ("Full", "بیمه فول درمان"),
    ]

    STATUS_CHOICES = [
        ("Disable", "غیرفعال"),
        ("Enable", "فعال"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="نام بیمه")
    type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, verbose_name="نوع بیمه"
    )
    status = models.CharField(
        max_length=13, choices=STATUS_CHOICES, verbose_name="وضعیت"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Insurance"
        verbose_name_plural = "Insurances"
        ordering = ["-created_date"]
        db_table = "insurances"
        indexes = [
            models.Index(fields=["type", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "type"], name="unique_insurance_name_type"
            )
        ]

    def __str__(self):
        return self.name


class News(models.Model):
    STATUS_CHOICES = [
        ("Disable", "غیرفعال"),
        ("Enable", "فعال"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name="عنوان")
    text = CKEditor5Field("Biography", config_name="default")
    pic = models.ImageField(
        upload_to="news/",
        default="news/news_def.png",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"],
                message="فقط فایل‌های تصویری با فرمت JPG, JPEG, PNG مجاز هستند.",
            )
        ],
        error_messages={
            "blank": "لطفاً یک عکس انتخاب کنید.",
            "invalid": "فایل انتخاب شده معتبر نیست.",
            "invalid_image": "فایل ارسالی خراب می‌باشد",
            "empty": "فایل بارگذاری شده خالی است.",
            "missing": "هیچ فایلی برای بارگذاری انتخاب نشده است.",
        },
    )
    status = models.CharField(choices=STATUS_CHOICES, default="Enable", max_length=15)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ["-created_date"]
        db_table = "News"
        indexes = [
            models.Index(fields=["created_date"]),
        ]

    def __str__(self):
        return self.title
