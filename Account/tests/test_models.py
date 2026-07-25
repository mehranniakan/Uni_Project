import pytest
from django.db import IntegrityError
from faker import Faker

from Account.models import User, Patient, Doctor, Reception, Supervisor, SubUser
from Clinic.models import DoctorServices
from Receptions.models import Insurances
from test_fixtures import (patient_user,
                           doctor_user,
                           active_patient_profile,
                           reception_user,
                           supervisor_user,
                           clinic_normal)

faker = Faker(["fa_IR"])


@pytest.mark.django_db
class TestAccountModels:

    def test_user_create(self):
        user = User.objects.create_user(
            username="1742054811",
            password="password123",
            first_name="مهران",
            last_name="نیاکان",
            sex='Male',
            birthdate='1995-10-24',
            role="patient",
            mobile_number="09120000000",
        )
        assert user.first_name == "مهران"
        assert user.last_name == "نیاکان"
        assert user.username == "1742054811"
        assert user.role == "patient"
        assert user.check_password("password123")

    def test_user_create_without_password(self):
        with pytest.raises(ValueError, match="Password is required"):
            User.objects.create_user(
                username="1234567890",
                password=None,
                first_name="مهران",
                last_name="نیاکان",
                sex='Male',
                birthdate='1995-10-24',
                role="patient",
                mobile_number="09120000000",
            )

    def test_user_patient_profile_create(self, patient_user):
        base_insur, _ = Insurances.objects.get_or_create(
            name='test_base_insur',
            type="Base",
        )
        supp_insur, _ = Insurances.objects.get_or_create(
            name='test_supp_insur',
            type="Supplementary",
        )
        full_insur, _ = Insurances.objects.get_or_create(
            name='test_full_insur',
            type="Full",
        )
        address = faker.address(),
        patient = Patient.objects.create(
            user=patient_user,
            insurance_base=base_insur,
            insurance_supp=supp_insur,
            insurance_full=full_insur,
            address=address,
            status="Active"
        )
        assert patient is not None
        assert patient.user == patient_user
        assert patient.insurance_base == base_insur
        assert patient.insurance_supp == supp_insur
        assert patient.insurance_full == full_insur
        assert patient.address == address
        assert patient.status == "Active"

    def test_user_patient_profile_create_without_user(self):
        with pytest.raises(IntegrityError):
            base_insur, _ = Insurances.objects.get_or_create(
                name='test_base_insur',
                type="Base",
            )
            supp_insur, _ = Insurances.objects.get_or_create(
                name='test_supp_insur',
                type="Supplementary",
            )
            full_insur, _ = Insurances.objects.get_or_create(
                name='test_full_insur',
                type="Full",
            )
            address = faker.address(),
            patient = Patient.objects.create(
                insurance_base=base_insur,
                insurance_supp=supp_insur,
                insurance_full=full_insur,
                address=address,
                status="Active"
            )

            assert patient is not None

    def test_user_doctor_profile_create(self, doctor_user, clinic_normal):
        service, _ = DoctorServices.objects.get_or_create(name='test_service')

        doctor = Doctor.objects.create(
            user=doctor_user,
            clinic=clinic_normal,
            speciality='best test doctor',
            super_speciality='best test doctor',
            description='test doctor description',
            pt_cap='50',
            status="Active"
        )
        doctor.services.set([service])

        assert doctor is not None
        assert doctor.user == doctor_user
        assert doctor.clinic == clinic_normal
        assert doctor.speciality == 'best test doctor'
        assert doctor.super_speciality == 'best test doctor'
        assert doctor.description == 'test doctor description'
        assert doctor.pt_cap == '50'
        assert doctor.status == "Active"
        assert doctor.services.filter(id=service.id).exists()

    def test_user_doctor_profile_create_without_user(self, clinic_normal):
        with pytest.raises(IntegrityError):
            service, _ = DoctorServices.objects.get_or_create(name='test_service')

            doctor = Doctor.objects.create(
                clinic=clinic_normal,
                speciality='best test doctor',
                super_speciality='best test doctor',
                description='test doctor description',
                pt_cap='50',
                status="Active"
            )
            doctor.services.set([service])

            assert doctor.user is None

    def test_user_reception_profile_create(self, reception_user, clinic_normal):
        reception = Reception.objects.create(
            user=reception_user,
            status="Active"
        )

        reception.privileges.set([clinic_normal])

        assert reception is not None
        assert reception.user == reception_user
        assert reception.privileges.filter(id=clinic_normal.id).exists()
        assert reception.status == "Active"

    def test_user_reception_profile_create_without_user(self, reception_user, clinic_normal):
        with pytest.raises(IntegrityError):
            reception = Reception.objects.create(
                status="Active"
            )

            reception.privileges.set([clinic_normal])

            assert reception is None

    def test_user_supervisor_profile_create(self, supervisor_user):
        supervisor = Supervisor.objects.create(
            user=supervisor_user,
            status="Active"
        )

        assert supervisor is not None
        assert supervisor.user == supervisor_user
        assert supervisor.status == "Active"

    def test_user_supervisor_profile_create_without_user(self):
        with pytest.raises(IntegrityError):
            supervisor = Supervisor.objects.create(
                status="Active"
            )

            assert supervisor is None

    def test_user_subuser_profile_create(self, active_patient_profile):
        sub_user = SubUser.objects.create(
            user=active_patient_profile,
            first_name='test_first_name',
            last_name='test_last_name',
            national_id='1234567890',
            relation='Siblings',
            birthdate="1995-10-24",
        )

        assert sub_user is not None
        assert sub_user.user == active_patient_profile
        assert sub_user.first_name == 'test_first_name'
        assert sub_user.last_name == 'test_last_name'
        assert sub_user.national_id == '1234567890'
        assert sub_user.relation == 'Siblings'
        assert sub_user.birthdate == '1995-10-24'

    def test_user_subuser_profile_create_without_user(self):

        with pytest.raises(IntegrityError):

            sub_user = SubUser.objects.create(
                first_name='test_first_name',
                last_name='test_last_name',
                national_id='1234567890',
                relation='Siblings',
                birthdate="1995-10-24",
            )

            assert sub_user is None
