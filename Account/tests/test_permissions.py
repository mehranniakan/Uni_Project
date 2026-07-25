import pytest
from django.urls import reverse



@pytest.mark.django_db
class TestAccountPermissions:

    login_url = reverse("login")
    signup_url = reverse("signup")
    profile_url = reverse("profile")
    sub_user_url = reverse("dependents_list")
    add_sub_user_url = reverse("add_dependents")

    def test_profile_without_login(self, client):
        response = client.get(self.profile_url)
        assert response.status_code == 302
        assert "login" in response.url


    def test_sub_user_list_without_login(self,
                                         client,
                                         patient_user,
                                         active_patient_profile):
        response = client.get(self.sub_user_url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_add_sub_user_without_login(self,
                                        client,
                                        patient_user,
                                        active_patient_profile):
        url = reverse('add_dependents')
        data = {
            "first_name": "مهران",
            "last_name": "نیاکان",
            "national_id": "1742054811",
            "birthdate": "1390/02/15",
            "relation": "Children"
        }

        response = client.post(url, data)
        assert response.status_code == 302
        assert "login" in response.url


    def test_edit_sub_user_without_login(self,
                                         client,
                                         patient_user,
                                         active_patient_profile,
                                         sub_user):
        url = reverse("edit_dependents",
                      kwargs={'pk': sub_user.id})
        data = {
            "first_name": "مهران",
            "last_name": "نیاکان",
            "national_id": "1742054811",
            "birthdate": "1390/02/15",
            "relation": "Children"
        }

        response = client.post(url, data)
        assert response.status_code == 302
        assert "login" in response.url


    def test_edit_account_without_login(self,
                                        client,
                                        patient_user):
        url = reverse("edit_account",
                      kwargs={'pk': patient_user.id})

        data = {
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

        response = client.post(url, data)
        assert response.status_code == 302
        assert "login" in response.url
