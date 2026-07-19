from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from persian_tools import national_id, phone_number
from persiantools.jdatetime import JalaliDate

from Account.models import User, SubUser, Patient
from Receptions.forms import name_cleaner
from Receptions.models import Insurances


class CustomSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")

    password2 = forms.CharField(widget=forms.PasswordInput, label="تکرار رمز عبور")

    birthdate = forms.CharField(
        label="تاریخ تولد",
        widget=forms.TextInput(
            attrs={
                "id": "birthdate-picker",
                "placeholder": "1403/01/01",
                "autocomplete": "off",
                "class": "date-input",
            }
        ),
    )

    insurance_base = forms.ModelChoiceField(
        required=False,
        queryset=Insurances.objects.filter(type="Base"),
        label="بیمه پایه",
    )

    insurance_supp = forms.ModelChoiceField(
        required=False,
        queryset=Insurances.objects.filter(type="Supplementary"),
        label="بیمه تکمیلی",
    )

    insurance_full = forms.ModelChoiceField(
        required=False,
        queryset=Insurances.objects.filter(type="Full"),
        label="بیمه فول درمان",
    )

    class Meta:
        model = User
        error_css_class = "has-error"
        required_css_class = "required-field"
        fields = [
            "first_name",
            "last_name",
            "username",
            "birthdate",
            "sex",
            "mobile_number",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_first_name(self):

        first_name = self.cleaned_data.get("first_name")

        first_name = name_cleaner(first_name, "نام")

        return first_name

    def clean_last_name(self):

        last_name = self.cleaned_data.get("last_name")

        last_name = name_cleaner(last_name, "نام خانوادگی")

        return last_name

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if national_id.validate(username):
            if User.objects.filter(username=username).exists():
                raise ValidationError("کاربری با این کد ملی در سیستم وجود دارد ")
            else:
                return username
        else:
            raise ValidationError("کدملی ارسالی معتبر نیست")

    def clean_mobile_number(self):
        phone = self.cleaned_data.get("mobile_number")

        if phone_number.validate(phone):
            return phone
        else:
            raise ValidationError("شماره تماس معتبر نیست")

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")

        birthdate = birthdate.split("/")
        if (
            JalaliDate(int(birthdate[0]), int(birthdate[1]), int(birthdate[2]))
            < JalaliDate.today()
        ):
            try:
                birthdate = JalaliDate(
                    int(birthdate[0]), int(birthdate[1]), int(birthdate[2])
                ).to_gregorian()
                return birthdate
            except ValueError:
                raise ValidationError("تاریخ معتبر نیست")
        else:
            raise ValidationError("تاریخ معتبر نیست")

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if password1:
            try:
                validate_password(password1)
            except ValidationError as e:
                error_map = {
                    "The password is too similar to the username.": "رمز عبور شما شبیه به کدملی است.",
                    "The password is too similar to the first name.": "رمز عبور شما شبیه به نام است.",
                    "The password is too similar to the last name.": "رمز عبور شما شبیه به نام خانوادگی است.",
                    "The password is too similar to the mobile number.": "رمز عبور شما شبیه به شماره موبایل است.",
                    "This password is too short. It must contain at least 8 characters.": "رمز عبور باید حداقل 8 کاراکتر باشد.",
                    "This password is too common.": "این رمز عبور بسیار رایج است.",
                    "This password is entirely numeric.": "رمز عبور نمی‌تواند فقط عدد باشد.",
                }

                persian_errors = []
                for error in e.messages:
                    # جایگزینی داینامیک برای min_length
                    if "%(8)d" in error:
                        for key, value in e.params.items():
                            error = error.replace("%%(%s)d" % key, str(value))

                    persian_errors.append(error_map.get(error, error))

                raise ValidationError(persian_errors)

        return password1

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password1", "رمزهای عبور مطابقت ندارند")
            self.add_error("password2", "رمزهای عبور مطابقت ندارند")

        if cleaned_data.get("insurance_full") and cleaned_data.get("insurance_supp"):
            self.add_error(
                "insurance_supp",
                "در صورت داشتن بیمه فول درمان بیمه تکمیلی را خالی بگذارید",
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

            Patient.objects.create(
                user=user,
                insurance_base=self.cleaned_data["insurance_base"],
                insurance_supp=self.cleaned_data["insurance_supp"],
                insurance_full=self.cleaned_data["insurance_full"],
            )

        return user


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        label="کدملی",
    )
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")

    class Meta:
        error_css_class = "has-error"
        required_css_class = "required-field"

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if national_id.validate(username):
            return username
        else:
            raise ValidationError("کدملی ارسالی معتبر نیست")

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)

            if user is None:
                raise ValidationError("نام کاربری یا رمز عبور اشتباه می باشد !")
            elif not user.is_active:
                raise ValidationError("حساب کاربری شما غیر فعال می باشد !")
            else:
                cleaned_data["user"] = user

        return cleaned_data


class EditAccount(forms.ModelForm):
    birthdate = forms.CharField(
        label="تاریخ تولد",
        widget=forms.TextInput(
            attrs={
                "id": "birthdate-picker",
                "placeholder": "1403/01/01",
                "autocomplete": "off",
                "class": "date-input",
            }
        ),
    )
    insurance_base = forms.ModelChoiceField(
        required=False,
        queryset=Insurances.objects.filter(type="Base"),
        label="بیمه پایه",
    )

    insurance_supp = forms.ModelChoiceField(
        required=False,
        queryset=Insurances.objects.filter(type="Supplementary"),
        label="بیمه تکمیلی",
    )

    insurance_full = forms.ModelChoiceField(
        required=False,
        queryset=Insurances.objects.filter(type="Full"),
        label="بیمه فول درمان",
    )
    address = forms.CharField(required=False, label="آدرس", widget=forms.Textarea())

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "mobile_number",
            "birthdate",
            "sex",
        ]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "username": "کدملی",
            "birthdate": "تاریخ تولد",
            "mobile_number": "موبایل",
            "sex": "جنسیت",
            "address": "آدرس",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.birthdate:
            self.initial["birthdate"] = JalaliDate.to_jalali(
                self.instance.birthdate
            ).strftime("%Y/%m/%d")

        if hasattr(self.instance, "patient"):
            patient = self.instance.patient

            self.initial["insurance_base"] = patient.insurance_base
            self.initial["insurance_supp"] = patient.insurance_supp
            self.initial["insurance_full"] = patient.insurance_full
            self.initial["address"] = patient.address

    def clean_first_name(self):

        first_name = self.cleaned_data.get("first_name")

        first_name = name_cleaner(first_name, "نام")

        return first_name

    def clean_last_name(self):

        last_name = self.cleaned_data.get("last_name")

        last_name = name_cleaner(last_name, "نام خانوادگی")

        return last_name

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if national_id.validate(username):
            return username
        else:
            raise ValidationError("کدملی وارد شده معتبر نمی باشد")

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get("mobile_number")

        if phone_number.validate(mobile_number):
            return mobile_number
        else:
            raise ValidationError("شماره موبایل وارد شده معتبر نمی باشد !")

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")

        try:
            y, m, d = map(int, birthdate.split("/"))
            jdate = JalaliDate(y, m, d)

            if jdate >= JalaliDate.today():
                raise ValidationError("تاریخ معتبر نیست")

            return jdate.to_gregorian()

        except Exception:
            raise ValidationError("فرمت تاریخ صحیح نیست")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("insurance_full") and cleaned_data.get("insurance_supp"):
            self.add_error(
                "insurance_supp",
                "در صورت داشتن بیمه فول درمان بیمه تکمیلی را خالی بگذارید",
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            with transaction.atomic():
                user.save()

                patient = user.patient

                patient.insurance_base = self.cleaned_data.get("insurance_base")
                patient.insurance_supp = self.cleaned_data.get("insurance_supp")
                patient.insurance_full = self.cleaned_data.get("insurance_full")
                patient.address = self.cleaned_data.get("address")

                patient.save()

        return user


class SubUserForm(forms.ModelForm):
    patient = None
    Action = None

    birthdate = forms.CharField(
        label="تاریخ تولد",
        widget=forms.TextInput(
            attrs={
                "id": "birthdate-picker",
                "placeholder": "1403/01/01",
                "autocomplete": "off",
                "class": "date-input",
            }
        ),
    )

    class Meta:
        model = SubUser
        fields = ["first_name", "last_name", "national_id", "birthdate", "relation"]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "national_id": "کدملی",
            "relation": "نسبت",
        }

    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop("patient", None)
        self.Action = kwargs.pop("Action", None)

        super().__init__(*args, **kwargs)

        if self.instance and self.instance.birthdate:
            self.initial["birthdate"] = JalaliDate.to_jalali(
                self.instance.birthdate
            ).strftime("%Y/%m/%d")

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        first_name = name_cleaner(first_name, "نام")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        last_name = name_cleaner(last_name, "نام خانوادگی")
        return last_name

    def clean_national_id(self):
        nat_id = self.cleaned_data.get("national_id")

        if national_id.validate(nat_id):
            return nat_id
        else:
            raise ValidationError("کدملی وارد شده معتبر نمی باشد")

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")
        try:
            y, m, d = map(int, birthdate.split("/"))
            jdate = JalaliDate(y, m, d)
        except Exception:
            raise ValidationError("فرمت تاریخ معتبر نیست")

        if jdate >= JalaliDate.today():
            raise ValidationError("تاریخ تولد باید قبل از امروز باشد")

        return jdate.to_gregorian()

    def clean(self):
        cleaned_data = super().clean()

        nat_id = cleaned_data.get("national_id")

        if self.Action == "Edit":
            if self.instance.national_id != nat_id:
                if User.objects.filter(username=nat_id).exists():
                    self.add_error(
                        "national_id",
                        "کاربری با این کدملی در سیستم قبلا ثبت نام کرده است !",
                    )

        else:
            if SubUser.objects.filter(user=self.patient).count() >= 10:
                self.add_error(None, "حداکثر تعداد افراد تحت تکفل 10 نفر می باشد!")

            if User.objects.filter(username=nat_id).exists():
                self.add_error(
                    "national_id",
                    "کاربری با این کدملی در سیستم قبلا ثبت نام کرده است !",
                )

        return cleaned_data

    def save(self, commit=True):

        sub_user = super().save(commit=False)
        sub_user.user = self.patient

        if commit:
            sub_user.save()

        return sub_user
