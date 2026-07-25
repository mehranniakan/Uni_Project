import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("National code is required")

        username = str(username).strip()

        if len(username) != 10 or not username.isdigit():
            raise ValueError("National code must be exactly 10 digits")

        if not password:
            raise ValueError("Password is required")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        extra_fields.setdefault("is_active", True)

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("patient", "کاربر"),
        ("doctor", "پزشک"),
        ("reception", "پذیرش"),
        ("supervisor", "سوپروایزر"),
    ]

    SEX_CHOICES = [
        ("Male", "مرد"),
        ("Female", "زن"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")

    first_name = models.CharField(max_length=30, verbose_name="نام")

    last_name = models.CharField(max_length=30, verbose_name="نام خانوادگی")

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        db_index=True,
        default="patient",
        verbose_name="نقش",
    )
    sex = models.CharField(
        choices=SEX_CHOICES, max_length=10, default="Male", verbose_name="جنسیت"
    )

    birthdate = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")

    mobile_number = models.CharField(max_length=14, verbose_name="موبایل")

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    email = None
    EMAIL_FIELD = None

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = "users"

        ordering = ["-created_date"]

        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Patient(models.Model):
    STATUS_CHOICES = [
        ("Active", "فعال"),
        ("Inactive", "غیرفعال"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient"
    )

    insurance_base = models.ForeignKey(
        "Receptions.Insurances",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="base_patients",
        verbose_name="بیمه پایه",
    )

    insurance_supp = models.ForeignKey(
        "Receptions.Insurances",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supp_patients",
        verbose_name="بیمه تکمیلی",
    )

    insurance_full = models.ForeignKey(
        "Receptions.Insurances",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="full_patients",
        verbose_name="بیمه فول درمان",
    )

    address = models.TextField(blank=True, default="")

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active",
        verbose_name="وضعیت فعالیت",
    )

    class Meta:
        db_table = "patients"
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return str(self.user)


class SubUser(models.Model):
    RELATION_CHOICES = [
        ("Siblings", "خواهر یا برادر"),
        ("Spouse", "همسر"),
        ("Children", "فرزندان"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(
        max_length=30,
        verbose_name="نام",
        error_messages={
            "max_length": "تعداد کاراکترها بیشتر از حد مجاز است",
            "blank": "این فیلد نمی‌تواند خالی باشد",
        },
    )

    last_name = models.CharField(
        max_length=30,
        verbose_name="نام خانوادگی",
        error_messages={
            "max_length": "تعداد کاراکترها بیشتر از حد مجاز است",
            "blank": "این فیلد نمی‌تواند خالی باشد",
        },
    )

    national_id = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="کدملی",
        error_messages={
            "max_length": "حداکثر کاراکتر مجاز 10 عدد می‌باشد",
            "blank": "این فیلد نمی‌تواند خالی باشد",
            "unique": "فردی با این کدملی در سیستم وجود دارد",
        },
    )

    relation = models.CharField(
        max_length=30, verbose_name="نسبت با کاربر", choices=RELATION_CHOICES
    )

    user = models.ForeignKey(
        Patient,
        related_name="sub_users",
        on_delete=models.CASCADE,
        verbose_name="کاربر اصلی",
    )

    birthdate = models.DateField(
        verbose_name="تاریخ تولد",
        error_messages={
            "invalid": "فرمت تاریخ نامعتبر است. لطفاً تاریخ را به صورت سال-ماه-روز وارد کنید.",
            "required": "تاریخ تولد الزامی است.",
        },
    )

    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "Sub User"
        verbose_name_plural = "Sub Users"
        db_table = "Sub_User"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["national_id"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Doctor(models.Model):
    STATUS_CHOICES = [
        ("Active", "فعال"),
        ("Inactive", "غیرفعال"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor"
    )

    clinic = models.ForeignKey(
        "Clinic.Clinics",
        on_delete=models.CASCADE,
        related_name="doctors",
        verbose_name="کلینیک محل فعالیت",
    )

    speciality = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="تخصص"
    )

    super_speciality = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="فوق تخصص"
    )

    services = models.ManyToManyField(
        "Clinic.DoctorServices", related_name="doctors", verbose_name="خدمات"
    )

    description = CKEditor5Field("Biography", config_name="default")

    pt_cap = models.PositiveIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(999)
        ],
        default=10,
        verbose_name="ظرفیت بیمار در روز")

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active",
        verbose_name="وضعیت فعالیت",
    )

    pic = models.ImageField(
        upload_to="docs/",
        default="docs/def.jpg",
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
    is_top = models.BooleanField(default=False, verbose_name="پزشکان برتر")

    is_popular = models.BooleanField(default=False, verbose_name="پزشکان محبوب")

    class Meta:
        db_table = "doctors"

        indexes = [
            models.Index(fields=["clinic"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return str(self.user)


class Reception(models.Model):
    STATUS_CHOICES = [
        ("Active", "فعال"),
        ("Inactive", "غیرفعال"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reception"
    )

    privileges = models.ManyToManyField(
        "Clinic.Clinics",
        verbose_name="دسترسی کلینیک‌ها",
        blank=True,
        related_name="receptions",
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active",
        verbose_name="وضعیت فعالیت",
    )

    class Meta:
        db_table = "receptions"

    def __str__(self):
        return str(self.user)


class Supervisor(models.Model):
    STATUS_CHOICES = [
        ("Active", "فعال"),
        ("Inactive", "غیرفعال"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="supervisor"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Active",
        verbose_name="وضعیت فعالیت",
    )

    class Meta:
        db_table = "supervisors"

    def __str__(self):
        return str(self.user)
