import pytest
from django.urls import reverse

from Account.models import SubUser


@pytest.mark.django_db
class TestAccountViews:
    login_url = reverse("login")
    signup_url = reverse("signup")
    sub_user_url = reverse("dependents_list")
    add_sub_user_url = reverse("add_dependents")

    def test_login_view_get(self, client):
        response = client.get(self.login_url)
        assert response.status_code == 200
        assert "account/login.html" in [t.name for t in response.templates]

    def test_login_success(self,
                           client,
                           patient_user):
        data = {
            "username": patient_user.username,
            "password": "password123"
        }
        response = client.post(self.login_url, data)
        # پس از ورود موفق باید به صفحه profile ریدایرکت شود
        assert response.status_code == 302
        assert response.url == reverse("profile")

    def test_login_failed_wrong_credentials(self,
                                            client,
                                            patient_user):
        data = {
            "username": patient_user.username,
            "password": "wrongpassword"
        }
        response = client.post(self.login_url, data)
        assert response.status_code == 200
        assert "form" in response.context
        assert response.context["form"].errors

    def test_login_rate_limiting(self, client):
        data = {"username": "1234567890",
                "password": "wrongpassword"}

        for i in range(11):
            response = client.post(self.login_url, data)
            if i >= 10:
                assert response.status_code == 403
            else:
                assert response.status_code in [200, 302]


    def test_signup_view_get(self, client):
        response = client.get(self.signup_url)
        assert response.status_code == 200
        assert "account/sign_up.html" in [t.name for t in response.templates]


    def test_signup_success(self, client):
        form_data = {
            'username': '1742054811',
            'first_name': 'مهران ',
            'last_name': 'نیاکان',
            'mobile_number': '09121112233',
            'birthdate': '1374/08/02',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'insurance_base': '',
            'insurance_supp': '',
            'insurance_full': '',
            'sex': 'Male'
        }

        response = client.post(self.signup_url, form_data)
        assert response.status_code == 302
        assert response.url == reverse("login")


    def test_signup_failed(self, client):
        form_data = {
            'username': '1742054812',
            'first_name': 'مهران ',
            'last_name': 'نیاکان',
            'mobile_number': '09120000000',
            'birthdate': '1374/08/02',
            'password1': 'StrongPassword123!',
            'password2': 'Strong',
            'insurance_base': '',
            'insurance_supp': '',
            'insurance_full': '',
            'sex': 'Male'
        }

        response = client.post(self.signup_url, form_data)
        assert response.status_code == 200
        assert response.context["form"].errors


    def test_signup_already_registered(self,
                                       client,
                                       patient_user):
        form_data = {
            'username': patient_user.username,
            'first_name': 'مهران ',
            'last_name': 'نیاکان',
            'mobile_number': '09120000000',
            'birthdate': '1374/08/02',
            'password1': 'StrongPassword123!',
            'password2': 'Strong',
            'insurance_base': '',
            'insurance_supp': '',
            'insurance_full': '',
            'sex': 'Male'
        }

        response = client.post(self.signup_url, form_data)
        assert response.status_code == 200
        assert response.context["form"].errors


    def test_sub_user_list_success(self,
                                   client,
                                   patient_user,
                                   active_patient_profile,
                                   sub_user):
        client.force_login(patient_user)
        response = client.get(self.sub_user_url)
        assert response.status_code == 200
        assert sub_user in response.context["subs"]
        assert "account/dependents.html" in [t.name for t in response.templates]


    def test_sub_user_create_success(self,
                                     client,
                                     patient_user,
                                     active_patient_profile):

        client.force_login(patient_user)

        data = {
            "first_name": "مهران",
            "last_name": "نیاکان",
            "national_id": "1742054811",
            "birthdate": "1390/02/15",
            "relation": "Children"
        }
        response = client.post(self.add_sub_user_url, data)
        assert response.status_code == 302
        assert response.url == reverse("dependents_list")
        assert SubUser.objects.filter(national_id="1742054811", user=active_patient_profile).exists()


    def test_sub_user_create_limit_exceeded(self,
                                            client,
                                            patient_user,
                                            active_patient_profile):
        client.force_login(patient_user)

        for i in range(10):
            SubUser.objects.create(
                user=active_patient_profile,
                first_name=f"عضو{i}",
                last_name="تست‌پرور",
                national_id=f"001111111{i}",
                birthdate="1395-01-01",
                relation="Child"
            )

        data = {
            "first_name": "عضو یازدهم",
            "last_name": "تست‌پرور",
            "national_id": "1742054811",
            "birthdate": "1395/01/01",
            "relation": "Child"
        }
        response = client.post(self.add_sub_user_url, data)
        assert response.status_code == 200
        form = response.context["form"]
        assert any("حداکثر تعداد افراد تحت تکفل 10 نفر می باشد!" in error for error in form.non_field_errors())


    def test_sub_user_update_page_success(self,
                                          client,
                                          patient_user,
                                          active_patient_profile,
                                          sub_user):

        client.force_login(patient_user)

        edit_sub_user_url = reverse("edit_dependents", kwargs={'pk': sub_user.id})

        response = client.get(edit_sub_user_url)
        assert response.status_code == 200
        assert 'first_name' in response.context["form"].fields
        assert 'last_name' in response.context["form"].fields
        assert 'relation' in response.context["form"].fields
        assert 'birthdate' in response.context["form"].fields


    def test_sub_user_update_success(self,
                                     client,
                                     patient_user,
                                     active_patient_profile,
                                     sub_user):

        client.force_login(patient_user)
        edit_sub_user_url = reverse("edit_dependents", kwargs={'pk': sub_user.id})
        data = {
            "first_name": "مهران",
            "last_name": "نیاکان",
            "national_id": sub_user.national_id,
            "birthdate": "1374/08/02",
            "relation": "Siblings"
        }
        response = client.post(edit_sub_user_url, data)
        assert response.status_code == 302
        assert response.url == reverse("dependents_list")


    def test_sub_user_update_rate_limit(self,
                                        client,
                                        patient_user,
                                        active_patient_profile,
                                        clear_cache_and_db_cleaner,
                                        sub_user):

        client.force_login(patient_user)

        edit_sub_user_url = reverse("edit_dependents", kwargs={'pk': sub_user.id})

        data = {
            "first_name": "mehran",
            "last_name": "niakan",
            "national_id": sub_user.national_id,
            "birthdate": "1374/08/02",
            "relation": "Siblings"
        }

        for i in range(11):

            response = client.post(edit_sub_user_url, data)

            if i < 10:
                assert response.status_code == 200
                assert response.context["form"].errors

            else:
                assert response.status_code == 403

    def test_user_update_page_success(self,
                                      client,
                                      patient_user, ):

        url = reverse("edit_account", kwargs={'pk': patient_user.id})
        client.force_login(patient_user)
        response = client.get(url)
        assert response.status_code == 200
        assert 'first_name' in response.context["form"].fields


    def test_user_update_success(self,
                                 client,
                                 active_patient_profile,
                                 patient_user, ):

        url = reverse("edit_account", kwargs={'pk': patient_user.id})
        client.force_login(patient_user)
        form_data = {
            'username': '1742054811',
            'first_name': 'مهران ',
            'last_name': 'نیاکان',
            'mobile_number': '09121112233',
            'birthdate': '1374/08/02',
            'insurance_base': '',
            'insurance_supp': '',
            'insurance_full': '',
            'sex': 'Male'
        }
        response = client.post(url, data=form_data)
        assert response.status_code == 302


    def test_user_update_rate_limit(self,
                                    client,
                                    active_patient_profile,
                                    clear_cache_and_db_cleaner,
                                    patient_user, ):

        url = reverse("edit_account", kwargs={'pk': patient_user.id})
        client.force_login(patient_user)
        form_data = {
            'username': '1742054811',
            'first_name': 'mehran',
            'last_name': 'niakan',
            'mobile_number': '09121112233',
            'birthdate': '1374/08/02',
            'insurance_base': '',
            'insurance_supp': '',
            'insurance_full': '',
            'sex': 'Male'
        }

        for i in range(11):
            response = client.post(url, data=form_data)
            if i < 10:
                assert response.status_code == 200
                assert response.context["form"].errors
            else:
                assert response.status_code == 403