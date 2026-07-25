# Account/backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class NationalCodeBackend(ModelBackend):
    """
    Backend سفارشی برای احراز هویت با کدملی
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        usermodel = get_user_model()

        if username is None:
            username = kwargs.get(usermodel.USERNAME_FIELD)

        try:
            # جستجو با کدملی
            user = usermodel.objects.get(username=username)
        except usermodel.DoesNotExist:
            return None



        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
    
