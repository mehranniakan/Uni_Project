# Account/adapters.py
import re

from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class NationalCodeAccountAdapter(DefaultAccountAdapter):


    def clean_username(self, username, shallow=False):

        if not re.match(r"^\d{10}$", username):
            raise ValidationError(_("کدملی باید ۱۰ رقم باشد"))


        if not self.validate_national_code(username):
            raise ValidationError(_("کدملی معتبر نیست"))

        return username

    def validate_national_code(self, code):

        invalid_codes = [
            "0000000000",
            "1111111111",
            "2222222222",
            "3333333333",
            "4444444444",
            "5555555555",
            "6666666666",
            "7777777777",
            "8888888888",
            "9999999999",
            "0123456789",
            "9876543210",
        ]

        if code in invalid_codes:
            return False

        try:
            sum_val = 0
            for i in range(9):
                sum_val += int(code[i]) * (10 - i)

            remainder = sum_val % 11
            last_digit = int(code[9])

            if remainder < 2:
                return last_digit == remainder
            else:
                return last_digit == (11 - remainder)
        except Exception:

            return False

    def save_user(self, request, user, form, commit=True):

        data = form.cleaned_data
        user.username = data.get("national_code")
        user.email = data.get("email")
        user.first_name = data.get("first_name", "")
        user.last_name = data.get("last_name", "")

        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()

        if commit:
            user.save()

        return user

    def get_login_redirect_url(self, request):
        return "/main/"
