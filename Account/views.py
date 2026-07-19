from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, FormView, ListView

from Account.forms import CustomSignupForm, CustomLoginForm, EditAccount, SubUserForm
from Account.models import User, SubUser


def forgot_password(request):
    return render(request, "lost-password.html")


class LoginView(FormView):
    form_class = CustomLoginForm
    template_name = "account/login.html"
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        login(self.request, form.cleaned_data.get("user"))
        messages.success(self.request, "ورود با موفقیت انجام شد")
        return super().form_valid(form)


class SignupView(FormView):
    form_class = CustomSignupForm
    template_name = "account/sign_up.html"
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "ثبت نام با موفقیت انجام شد")
        return super().form_valid(form)


class SubUserListView(ListView, LoginRequiredMixin):
    model = SubUser
    template_name = "account/dependents.html"
    context_object_name = "subs"

    def get_queryset(self):
        return SubUser.objects.filter(user=self.request.user.patient)


class AdminUserUpdateView(UpdateView, LoginRequiredMixin):
    model = User
    form_class = EditAccount
    template_name = "account/edit_account.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات اکانت شما با موفقیت اصلاح شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SubUserUpdateView(UpdateView, LoginRequiredMixin):
    model = SubUser
    form_class = SubUserForm
    template_name = "account/add&edit_dependent.html"
    success_url = reverse_lazy("dependents_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["patient"] = self.request.user.patient
        kwargs["Action"] = "Edit"
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات فرد تحت تکفل با موفقیت اصلاح شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class SubUserCreateView(CreateView, LoginRequiredMixin):
    model = SubUser
    form_class = SubUserForm
    template_name = "account/add&edit_dependent.html"
    success_url = reverse_lazy("dependents_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["patient"] = self.request.user.patient
        kwargs["Action"] = "Add"
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "فرد تحت تکفل با موفقیت ثبت شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@login_required
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("main")
