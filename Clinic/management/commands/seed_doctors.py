import random

from django.core.management.base import BaseCommand
from faker import Faker

from Account.models import Doctor, User
from Clinic.models import Clinics, DoctorServices

fake = Faker(["fa_IR"])


class Command(BaseCommand):
    help = "Seed database with test doctors"

    def handle(self, *args, **kwargs):

        clinic_names = [
            "قلب",
            "مغز و اعصاب",
            "ارتوپدی",
            "پوست و مو",
            "چشم",
            "آزمایشگاه مرکزی",
            "فیزیوتراپی",
            "مداخلات خواب",
            "سونوگرافی",
            "اورولوژی",
            "خون و آنکولوژی",
            "بیماری های عفونی",
            "جراح عمومی",
            "زنان و زایمان",
            "گوارش و کبد",
            "اطفال",
            "داخلی",
            "عمومی",
            "گوش و حلق و بینی",
        ]

        clinics = []
        for name in clinic_names:
            clinic, _ = Clinics.objects.get_or_create(
                name=name, defaults={"type": "normal"}
            )
            clinics.append(clinic)

        self.stdout.write(self.style.SUCCESS("Clinics created ✅"))

        service_names = [
            "ویزیت تخصصی",
            "مشاوره آنلاین",
            "نوار قلب",
            "سونوگرافی",
            "آزمایش خون",
            "تست تراکم استخوان",
            "آندوسکوپی",
            "اسپیرومتری",
            "اکو قلب",
            "تست عصب و عضله",
            "کلونوسکوپی",
            "MRI",
            "OPG",
        ]

        services = []
        for name in service_names:
            service, _ = DoctorServices.objects.get_or_create(name=name)
            services.append(service)

        self.stdout.write(self.style.SUCCESS("Services created ✅"))

        for _ in range(30):
            national_code = str(random.randint(1000000000, 9999999999))

            user = User.objects.create_user(
                username=str(national_code),
                password="12345678",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role="doctor",
                sex=random.choice(["Male", "Female"]),
                mobile_number="09" + str(random.randint(100000000, 999999999)),
            )

            doctor = Doctor.objects.create(
                user=user,
                clinic=random.choice(clinics),
                speciality=random.choice(
                    [
                        "قلب و عروق",
                        "مغز و اعصاب",
                        "ارتوپدی",
                        "پوست و مو",
                        "چشم پزشکی",
                        None,
                    ]
                ),
                super_speciality=random.choice(
                    ["فلوشیپ جراحی قلب", "فلوشیپ ستون فقرات", "فلوشیپ لیزر پوست", None]
                ),
                description=fake.text(),
                pt_cap=random.randint(5, 30),
                status="Active",
            )

            doctor.services.set(random.sample(services, random.randint(1, 3)))

        self.stdout.write(self.style.SUCCESS("Doctors created ✅"))
