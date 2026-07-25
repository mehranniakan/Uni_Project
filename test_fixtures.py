# conftest.py
from django.core.cache import cache
import random
from faker import Faker
import pytest
from datetime import date, time
from Account.models import (User,
                            Patient,
                            Doctor,
                            Reception,
                            SubUser)
from Clinic.models import Clinics
from Receptions.models import Insurances
from Schedule.models import Schedule

faker = Faker(["fa_IR"])

@pytest.fixture(autouse=True)
def clear_cache_and_db_cleaner():
    cache.clear()
    yield
    cache.clear()

@pytest.fixture
def patient_user(db):
    return User.objects.create_user(
        username="1111111111",
        password="password123",
        first_name="tester",
        last_name="tester",
        sex='Male',
        birthdate='1995-10-24',
        role="patient",
        mobile_number="09120000000",
        is_staff=False,
        is_active=True,
    )

@pytest.fixture
def patient_user_disable(db):
    return User.objects.create_user(
        username="1111111111",
        password="password123",
        first_name="tester",
        last_name="tester",
        sex='Male',
        birthdate='1995-10-24',
        role="patient",
        mobile_number="09120000000",
        is_staff=False,
        is_active=False,
    )


@pytest.fixture
def reception_user(db):
    return User.objects.create_user(
        username="2222222222",
        password="password123",
        first_name="tester",
        last_name="tester",
        role="reception",
        mobile_number="09120000001",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def reception_user_disable(db):
    return User.objects.create_user(
        username="2222222222",
        password="password123",
        first_name="tester",
        last_name="tester",
        role="reception",
        mobile_number="09120000001",
        is_staff=True,
        is_active=False,
    )


@pytest.fixture
def supervisor_user(db):
    return User.objects.create_user(
        username="3333333333",
        password="password123",
        first_name="tester",
        last_name="tester",
        role="supervisor",
        mobile_number="09120000002",
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def supervisor_user_disable(db):
    return User.objects.create_user(
        username="3333333333",
        password="password123",
        first_name="tester",
        last_name="tester",
        role="supervisor",
        mobile_number="09120000002",
        is_staff=True,
        is_active=False,
    )


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        username="4444444444",
        password="password123",
        first_name="tester",
        last_name="tester",
        role="doctor",
        mobile_number="09120000003",
        is_staff=True,
        is_active=True,
    )

@pytest.fixture
def sub_user(db,active_patient_profile):
    return SubUser.objects.create(
        national_id="4444444444",
        user=active_patient_profile,
        first_name="tester",
        last_name="tester",
        birthdate = '1995-10-24',
        relation='Siblings'
    )

@pytest.fixture
def doctor_user_disable(db):
    return User.objects.create_user(
        username="4444444444",
        password="password123",
        first_name="tester",
        last_name="tester",
        role="doctor",
        mobile_number="09120000003",
        is_staff=True,
        is_active=False,
    )



@pytest.fixture
def active_patient_profile(db, patient_user):
    base_insur,_ = Insurances.objects.get_or_create(
        name = 'test_base_insur',
        type="Base",
    )
    supp_insur,_ = Insurances.objects.get_or_create(
        name = 'test_supp_insur',
        type="Supplementary",
    )
    full_insur,_ = Insurances.objects.get_or_create(
        name = 'test_full_insur',
        type="Full",
    )

    return Patient.objects.create(
        user=patient_user,
        insurance_base=base_insur,
        insurance_supp=supp_insur,
        insurance_full=full_insur,
        address=faker.address(),
        status="Active"
    )

@pytest.fixture
def inactive_patient_profile(db, patient_user):
    base_insur,_ = Insurances.objects.get_or_create(
        name='test_base_insur',
        type="Base",
    )
    supp_insur,_ = Insurances.objects.get_or_create(
        name='test_supp_insur',
        type="Supplementary",
    )
    full_insur,_ = Insurances.objects.get_or_create(
        name='test_full_insur',
        type="Full",
    )

    return Patient.objects.create(
        user=patient_user,
        insurance_base=base_insur,
        insurance_supp=supp_insur,
        insurance_full=full_insur,
        address=faker.address(),
        status="Inactive"
    )



@pytest.fixture
def active_doctor_profile(db, doctor_user):
    return Doctor.objects.create(
        user=doctor_user,
        clinic=random.choice(Clinics.objects.all()),
        speciality=faker.text(),
        super_speciality=faker.text(),
        services=faker.address(),
        description=faker.lorem_ipsum(),
        pt_cap=random.randint(10, 100),
        pic = faker.image_url(),
        status="Active"

    )

@pytest.fixture
def inactive_doctor_profile(db, doctor_user):
    return Doctor.objects.create(
        user=doctor_user,
        clinic=random.choice(Clinics.objects.all()),
        speciality=faker.text(),
        super_speciality=faker.text(),
        services=faker.address(),
        description=faker.lorem_ipsum(),
        pt_cap=random.randint(10, 100),
        pic=faker.image_url(),
        status="Inactive"
    )



@pytest.fixture
def active_reception_profile_heart_and_inner(db, reception_user):
    inner_clinic, _ = Clinics.objects.get_or_create(
        name="داخلی",
        defaults={"type": "normal"}
    )
    heart_clinic, _ = Clinics.objects.get_or_create(
        name="قلب",
        defaults={"type": "normal"}
    )

    reception = Reception.objects.create(
        user=reception_user,
        status="active"
    )
    reception.privileges.add(inner_clinic, heart_clinic)

    return reception

@pytest.fixture
def inactive_reception_profile_heart_and_inner(db, reception_user):
    inner_clinic, _ = Clinics.objects.get_or_create(
        name='قلب',
        defaults={"type": "normal"}
    )

    heart_clinic, _ = Clinics.objects.get_or_create(
        name="قلب",
        defaults={"type": "normal"}
    )

    reception = Reception.objects.create(
        user=reception_user,
        status="inactive"
    )
    reception.privileges.add(inner_clinic, heart_clinic)

    return reception



@pytest.fixture
def clinic_normal(db):
    return Clinics.objects.create(name="Main Clinic", type="normal")

@pytest.fixture
def clinic_para(db):
    return Clinics.objects.create(name="Main Clinic", type="paraclinic")


@pytest.fixture
def open_schedule(db, active_doctor_profile):
    return Schedule.objects.create(
        doctor=active_doctor_profile,
        start_time=time(9, 0),
        end_time=time(10, 0),
        schedule_date=date.today(),
        status="Open",
    )


@pytest.fixture
def closed_schedule(db, active_doctor_profile):
    return Schedule.objects.create(
        doctor=active_doctor_profile,
        start_time=time(11, 0),
        end_time=time(12, 0),
        schedule_date=date.today(),
        status="Closed",
    )
