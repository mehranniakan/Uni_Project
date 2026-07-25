import pytest

from Account.forms import CustomSignupForm, SubUserForm, CustomLoginForm, EditAccount

@pytest.mark.django_db
class TestAccountForms:

    def test_signup_form_valid_data(self):

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
        form = CustomSignupForm(data=form_data)
        assert form.is_valid()


    def test_signup_form_invalid_data(self):
        form_data = {
            'username': '123',
            'first_name': 'مهران ',
            'last_name': 'نیاکان',
            'mobile_number': '123',
            'birthdate': 1995-10-24,
            'password1': 'StrongPassword123!',
            'password2': '123',
            'insurance_base' : '',
            'insurance_supp': '',
            'insurance_full': '',
            'sex': 'Male'
        }
        form = CustomSignupForm(data=form_data)

        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'mobile_number' in form.errors
        assert 'password1' in form.errors
        assert 'birthdate' in form.errors


    def test_login_form_valid_data(self,patient_user):
        form_data = {
            'username': patient_user.username,
            'password': 'password123'
        }

        form = CustomLoginForm(data=form_data)

        assert form.is_valid()


    def test_login_form_invalid_username(self,patient_user):
        form_data = {
            'username': '1234567890',
            'password': 'password123'
        }

        form = CustomLoginForm(data=form_data)

        assert not form.is_valid()
        assert 'username' in form.errors


    def test_login_form_disable_user(self, patient_user_disable):

        form_data = {
            'username': patient_user_disable.username,
            'password': 'password123'
        }

        form = CustomLoginForm(data=form_data)

        assert not form.is_valid()
        assert '__all__' in form.errors


    def test_login_form_wrong_credential(self,patient_user):
        form_data = {
            'username': patient_user.username,
            'password': '123456789'
        }

        form = CustomLoginForm(data=form_data)

        assert not form.is_valid()
        assert '__all__' in form.errors


    def test_edit_account_form_valid_data(self):
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

        form = EditAccount(data=form_data)
        assert form.is_valid()


    def test_edit_account_form_invalid_data(self):
        form_data = {
            'username': '123',
            'first_name': 'مهران ',
            'last_name': 'نیاکان',
            'mobile_number': '123',
            'birthdate': 1995-10-24,
            'insurance_base' : '',
            'insurance_supp': '',
            'insurance_full': '',
            'sex': 'Male'
        }

        form = EditAccount(data=form_data)
        assert not form.is_valid()
        assert 'username' in form.errors
        assert 'mobile_number' in form.errors
        assert 'birthdate' in form.errors


    def test_add_subuser_form_valid_data(self, active_patient_profile):

        form_data = {
            'first_name': 'مهران',
            'last_name':'نیاکان',
            'national_id':'2222222222',
            'relation':'Siblings',
            'birthdate':'1374/08/02',
        }

        form = SubUserForm(data=form_data, Action='Add', patient=active_patient_profile)
        assert form.is_valid()


    def test_add_subuser_form_invalid_data(self, active_patient_profile):

        form_data = {
            'first_name': 'مهران',
            'last_name':'نیاکان',
            'national_id':'1234567890',
            'relation':'Siblings',
            'birthdate':'1374/08/02',
        }

        form = SubUserForm(data=form_data, Action='Add', patient=active_patient_profile)
        assert not form.is_valid()
        assert 'national_id' in form.errors


    def test_edit_subuser_form_valid_data(self, active_patient_profile):

        form_data = {
            'first_name': 'مهران',
            'last_name':'نیاکان',
            'national_id':'2222222222',
            'relation':'Siblings',
            'birthdate':'1374/08/02',
        }

        form = SubUserForm(data=form_data, Action='Edit', patient=active_patient_profile)
        assert form.is_valid()

