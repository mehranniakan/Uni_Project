import uuid

from django.test import TestCase

from Clinic.models import Doctor, Clinics, DoctorServices


# Create your tests here.


class DoctorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 1️⃣ ساخت کلینیک تستی
        clinic = Clinics.objects.create(name="کلینیک مرکزی")

        # 2️⃣ ساخت سرویس‌ها
        services = DoctorServices.objects.bulk_create(
            [DoctorServices(name=f"Service {i}") for i in range(5)]
        )

        # 3️⃣ ساخت دکترها (bulk)
        doctors = [
            Doctor(
                id=uuid.uuid4(),
                first_name="پریسا",
                last_name="امینی {i}",
                clinic=clinic,
                speciality="قلب",
                super_speciality="قلب و عروق",
                description="توضیحات تستی",
                pt_cap=20,
                sex="Male",
                status="Active",
                # برای ImageField لازم نیست فایل واقعی بدی چون default داری
            )
            for i in range(1000)
        ]

        created_doctors = Doctor.objects.bulk_create(doctors)

        # 4️⃣ افزودن ManyToMany بعد از bulk_create
        for doctor in created_doctors:
            doctor.services.set(services)

    def test_doctor_count(self):
        self.assertEqual(Doctor.objects.count(), 1000)
