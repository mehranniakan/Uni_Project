import re

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django_select2.forms import ModelSelect2Widget
from jdatetime import timedelta
from persian_tools import national_id, phone_number
from persiantools.jdatetime import JalaliDate

from Account.models import User, Doctor, Patient, Supervisor, Reception
from Clinic.models import Clinics, DoctorServices
from Receptions.models import Insurances, News
from Schedule.models import Schedule


## Custom Widgets & functions
class DoctorWidget(ModelSelect2Widget):
    model = User

    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
    ]

    max_results = 10

    attrs = {
        "data-placeholder": "نام دکتر را تایپ کنید...",
        "data-minimum-input-length": 1,
        "style": "width:100%",
    }
    queryset = User.objects.filter(role="doctor", is_active="True")


def name_cleaner(name, usage):
    persian_regex = r"^[\u0600-\u06FF0-9۰-۹\s\-\(\)\/]+$"

    name = name

    cleaned = name.strip()

    if not cleaned:
        raise ValidationError("این فیلد نمی‌تواند خالی باشد.")

    if not re.match(persian_regex, cleaned):
        raise ValidationError("لطفاً فقط با حروف فارسی تایپ کنید.")

    if len(cleaned) < 2:
        raise ValidationError(f" طول {usage} خیلی کوتاه است.")

    if len(cleaned) > 50:
        raise ValidationError(f" طول {usage} بیش از حد مجاز است.")

    return cleaned


## Forms
class DoctorForm(forms.ModelForm):
    Action = None

    first_name = forms.CharField(label="نام")

    last_name = forms.CharField(label="نام خانوادگی")

    clinic = forms.ModelChoiceField(
        label="کلینیک محل فعالیت", queryset=Clinics.objects.all()
    )

    password = forms.CharField(
        label="پسورد جدید", widget=forms.PasswordInput(), required=False
    )

    confirm_password = forms.CharField(
        label="تکرار پسورد", widget=forms.PasswordInput(), required=False
    )

    speciality = forms.CharField(
        label="تخصص",
    )

    super_speciality = forms.CharField(
        label="فوق تخصص",
    )

    services = forms.ModelMultipleChoiceField(
        label="خدمات",
        queryset=DoctorServices.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "service-checkbox"}),
    )
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

    pt_cap = forms.IntegerField(
        label="تعداد نوبت در روز",
    )

    pic = forms.ImageField(
        label="تصویر پروفایل",
    )

    is_active = forms.TypedChoiceField(
        label="وضعیت فعالیت",
        choices=[(True, "فعال"), (False, "غیرفعال")],
        coerce=lambda x: x == "True",
        widget=forms.Select(),
    )
    is_top = forms.BooleanField(label="پزشک برتر", required=False)

    is_popular = forms.BooleanField(label="پزشک محبوب", required=False)

    class Meta:
        model = User
        error_css_class = "has-error"
        required_css_class = "required-field"
        fields = [
            "first_name",
            "last_name",
            "username",
            "sex",
            "mobile_number",
            "birthdate",
            "is_active",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "نام", "dir": "rtl"}
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "نام خانوادگی",
                    "dir": "rtl",
                }
            ),
            "clinic": forms.Select(attrs={"class": "form-select", "dir": "rtl"}),
            "speciality": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "تخصص", "dir": "rtl"}
            ),
            "super_speciality": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "فوق تخصص", "dir": "rtl"}
            ),
            "pt_cap": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "تعداد بیمار در روز",
                    "dir": "rtl",
                }
            ),
            "sex": forms.Select(attrs={"class": "form-select", "dir": "rtl"}),
            "services": forms.CheckboxSelectMultiple(
                attrs={"class": "service-checkbox"}
            ),
            "pic": forms.FileInput(attrs={"class": "form-file-input"}),
        }
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "username": "کدملی",
            "sex": "جنسیت",
            "pic": "عکس پزشک",
            "is_active": "وضعیت فعالیت",
        }

    def __init__(self, *args, **kwargs):

        self.Action = kwargs.pop("Action", None)

        super().__init__(*args, **kwargs)

        self.fields["speciality"].required = False
        self.fields["super_speciality"].required = False
        self.fields["birthdate"].required = False
        self.fields["pic"].required = False

        if self.instance and self.instance.birthdate:
            self.initial["birthdate"] = JalaliDate.to_jalali(
                self.instance.birthdate
            ).strftime("%Y/%m/%d")

        if self.Action == "Edit":
            doctor = getattr(self.instance, "doctor", None)
            self.initial["clinic"] = doctor.clinic
            self.initial["services"] = doctor.services.all()
            self.initial["pt_cap"] = doctor.pt_cap
            self.initial["status"] = doctor.status
            self.initial["speciality"] = doctor.speciality
            self.initial["super_speciality"] = doctor.super_speciality
            self.initial["pic"] = doctor.pic

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

    def clean_pic(self):
        pic = self.cleaned_data.get("pic")

        if pic and hasattr(pic, "content_type"):
            allowed_types = ["image/jpeg", "image/png", "image/webp"]

            if pic.content_type not in allowed_types:
                raise forms.ValidationError("فرمت تصویر مجاز نیست")

            if pic.size > 5 * 1024 * 1024:
                raise forms.ValidationError("حجم تصویر نباید بیشتر از 5 مگابایت باشد")

        return pic

    def clean_pt_cap(self):
        pt_cap = self.cleaned_data.get("pt_cap")

        if type(pt_cap) is not int:
            raise ValidationError("باید مقداری عددی وارد کنید")

        if pt_cap < 0 or pt_cap > 1000:
            raise ValidationError("مقدار وارد شده معتبر نمی باشد ")

        return pt_cap

    def clean_clinic(self):
        clinic = self.cleaned_data.get("clinic")
        return clinic

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        clinic = cleaned_data.get("clinic")

        check_dup_doc = User.objects.filter(username=username, doctor__clinic=clinic)

        if self.instance.pk:
            check_dup_doc = check_dup_doc.exclude(pk=self.instance.pk)

        if check_dup_doc.exists():
            raise ValidationError("دکتری با این کدملی در این کلینیک وجود دارد!")

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=False)

            if self.cleaned_data.get("password"):
                user.set_password(self.cleaned_data.get("password"))

            user.role = "doctor"

            if commit:
                user.save()

            self.save_m2m()

            if self.Action == "Edit":
                doctor = user.doctor

                doctor.clinic = self.cleaned_data.get("clinic")
                doctor.speciality = self.cleaned_data.get("speciality")
                doctor.super_speciality = self.cleaned_data.get("super_speciality")
                doctor.pt_cap = self.cleaned_data.get("pt_cap")
                doctor.is_top = self.cleaned_data.get("is_top")
                doctor.is_popular = self.cleaned_data.get("is_popular")
                doctor.status = "Active"

                pic = self.cleaned_data.get("pic")

                if pic:
                    doctor.pic = pic

                doctor.save()

                doctor.services.set(self.cleaned_data.get("services"))

            else:
                doctor = Doctor.objects.create(
                    user=user,
                    clinic=self.cleaned_data.get("clinic"),
                    speciality=self.cleaned_data.get("speciality"),
                    super_speciality=self.cleaned_data.get("super_speciality"),
                    pt_cap=self.cleaned_data.get("pt_cap"),
                    status="Active",
                    is_top=self.cleaned_data.get("is_top"),
                    is_popular=self.cleaned_data.get("is_popular"),
                    pic=self.cleaned_data.get("pic"),
                )

                doctor.services.set(self.cleaned_data.get("services"))

            return user


class ScheduleForm(forms.ModelForm):
    start_time = forms.TimeField(
        label="زمان حضور",
        widget=forms.TextInput(attrs={"class": "timepicker", "autocomplete": "off"}),
        input_formats=["%H:%M"],
    )

    end_time = forms.TimeField(
        label="زمان خاتمه",
        widget=forms.TextInput(attrs={"class": "timepicker", "autocomplete": "off"}),
        input_formats=["%H:%M"],
    )
    schedule_date = forms.CharField(
        label="تاریخ برنامه",
        widget=forms.TextInput(
            attrs={
                "class": "persian-datepicker-input",
                "id": "birthdate-picker",
                "placeholder": "1403/01/01",
                "autocomplete": "off",
                "readonly": True,
            }
        ),
    )

    class Meta:
        model = Schedule
        fields = [
            "doctor",
            "schedule_date",
            "start_time",
            "end_time",
            "status",
        ]
        labels = {
            "doctor": "دکتر",
            "schedule_date": "تاریخ برنامه",
            "start_time": "زمان حضور",
            "end_time": "زمان اتمام",
            "status": "وضعیت",
        }
        widgets = {"doctor": DoctorWidget()}

    def clean_schedule_date(self):
        schedule_date = self.cleaned_data.get("schedule_date")

        schedule_date = schedule_date.split("/")
        current_date = JalaliDate(
            int(schedule_date[0]), int(schedule_date[1]), int(schedule_date[2])
        )
        today = JalaliDate.today()
        tomorrow = JalaliDate.today() + timedelta(days=1)

        if today <= current_date <= tomorrow:
            try:
                schedule_date = JalaliDate(
                    int(schedule_date[0]), int(schedule_date[1]), int(schedule_date[2])
                ).to_gregorian()
                return schedule_date
            except ValueError:
                raise ValidationError("تاریخ معتبر نیست")
        else:
            raise ValidationError("فقط تاریخ امروز و فردا قابل انتخاب می باشد ")

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("start_time") and cleaned_data.get("end_time"):
            if cleaned_data.get("start_time") > cleaned_data.get("end_time"):
                raise ValidationError("بازه ساعت انتخابی جابجا است !")

            if cleaned_data.get("start_time") == cleaned_data.get("end_time"):
                raise ValidationError("ساعت شروع و پایان یکی است !")

    def save(self, commit=True):
        schedule = super().save(commit=False)

        if commit:
            schedule.save()
        return schedule


class ClinicForm(forms.ModelForm):
    class Meta:
        model = Clinics
        fields = ["name", "type"]
        labels = {"name": "نام کلینیک", "type": "نوع کلینیک"}

    def clean_name(self):
        name = self.cleaned_data.get("name")
        name = name_cleaner(name, "نام")
        return name


class EditUsersForm(forms.ModelForm):
    old_role = None
    new_role = None

    password = forms.CharField(
        label="پسورد جدید", widget=forms.PasswordInput, required=False
    )

    confirm_password = forms.CharField(
        label="تکرار پسورد", widget=forms.PasswordInput, required=False
    )
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

    address = forms.TextInput()

    privileges = forms.ModelMultipleChoiceField(
        label="سطح دسترسی",
        queryset=Clinics.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    is_active = forms.TypedChoiceField(
        label="وضعیت فعالیت",
        choices=[(True, "فعال"), (False, "غیرفعال")],
        coerce=lambda x: x == "True",
        widget=forms.Select,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "role",
            "mobile_number",
            "birthdate",
            "sex",
            "is_active",
        ]
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "username": "کدملی",
            "role": "سمت",
            "birthdate": "تاریخ تولد",
            "mobile_number": "موبایل",
            "sex": "جنسیت",
            "is_active": "وضعیت فعالیت",
        }
        widgets = {
            "is_active": forms.RadioSelect(
                choices=[(True, "فعال"), (False, "غیرفعال")]
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["role"].choices = [
            choice for choice in self.fields["role"].choices if choice[0] != "doctor"
        ]

        self.old_role = self.instance.role if self.instance.pk else None

        if self.instance and (
                self.instance.role == "supervisor" or self.instance.role == "patient"
        ):
            self.fields.pop("privileges", None)
            self.fields.pop("insurance_base", None)
            self.fields.pop("insurance_supp", None)
            self.fields.pop("insurance_full", None)
            self.fields.pop("address", None)
        else:
            self.fields.pop("insurance_base", None)
            self.fields.pop("insurance_supp", None)
            self.fields.pop("insurance_full", None)
            self.fields.pop("address", None)

        optional_fields = [
            "password",
            "confirm_password",
        ]

        for field in optional_fields:
            self.fields[field].required = False

            if self.instance and self.instance.birthdate:
                self.initial["birthdate"] = JalaliDate.to_jalali(
                    self.instance.birthdate
                ).strftime("%Y/%m/%d")

        self.order_fields(
            [
                "first_name",
                "last_name",
                "username",
                "role",
                "mobile_number",
                "sex",
                "password",
                "confirm_password",
                "is_active",
                "privileges",
                "birthdate",
            ]
        )

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
        except Exception:
            raise ValidationError("فرمت تاریخ معتبر نیست")

        if jdate >= JalaliDate.today():
            raise ValidationError("تاریخ تولد باید قبل از امروز باشد")

        return jdate.to_gregorian()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("پسوردها یکسان نیستند")

        return cleaned_data

    def save(self, commit=True):

        user = super().save(commit=False)

        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data.get("password"))

        if commit:
            with transaction.atomic():
                new_role = self.cleaned_data.get("role")

                user.save()
                self.save_m2m()

                if self.old_role != new_role:
                    self.role_change_handeler(user, new_role, self.old_role)
        return user

    def role_change_handeler(self, user, new_role, old_role):
        role_model = {
            "patient": Patient,
            "supervisor": Supervisor,
            "reception": Reception,
        }

        new_model = role_model.get(new_role)
        old_model = role_model.get(old_role)

        if old_model:
            old_model.objects.filter(user=user).update(status="Inactive")

        if new_model:
            obj, create = new_model.objects.get_or_create(user=user)
            obj.status = "Active"
            obj.save()


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurances
        fields = ["name", "type", "status"]
        labels = {"name": "نام بیمه", "type": "نوع بیمه", "status": "وضعیت"}

    def clean_name(self):
        name = self.cleaned_data.get("name")

        name = name_cleaner(name, "نام")

        return name

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ["title", "text", "pic"]
        labels = {"title": "عنوان", "text": "متن", "pic": "تصویر"}
