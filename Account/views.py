from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, FormView, ListView
from django_ratelimit.decorators import ratelimit
from Account.forms import CustomSignupForm, CustomLoginForm, EditAccount, SubUserForm
from Account.models import User, SubUser
from django.utils.decorators import method_decorator


def forgot_password(request):
    return render(request, "lost-password.html")


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='100/m', method='GET', block=True), name='dispatch')
class LoginView(FormView):
    form_class = CustomLoginForm
    template_name = "account/login.html"
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        login(self.request, form.cleaned_data.get("user"))
        messages.success(self.request, "ورود با موفقیت انجام شد")
        return super().form_valid(form)


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='100/m', method='GET', block=True), name='dispatch')
class SignupView(FormView):
    form_class = CustomSignupForm
    template_name = "account/sign_up.html"
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "ثبت نام با موفقیت انجام شد")
        return super().form_valid(form)


@method_decorator(ratelimit(key='ip', rate='100/m', method='GET', block=True), name='dispatch')
class SubUserListView(LoginRequiredMixin, ListView):
    model = SubUser
    template_name = "account/dependents.html"
    http_method_names = ["get"]
    context_object_name = "subs"

    def get_queryset(self):
        return SubUser.objects.filter(user=self.request.user.patient)


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='100/m', method='GET', block=True), name='dispatch')
class AdminUserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditAccount
    http_method_names = ["get", "post"]
    template_name = "account/edit_account.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات اکانت شما با موفقیت اصلاح شد ! ")
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='100/m', method='GET', block=True), name='dispatch')
class SubUserUpdateView(LoginRequiredMixin, UpdateView):
    model = SubUser
    form_class = SubUserForm
    http_method_names = ["get", "post"]
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


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='dispatch')
@method_decorator(ratelimit(key='ip', rate='100/m', method='GET', block=True), name='dispatch')
class SubUserCreateView(LoginRequiredMixin, CreateView):
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
