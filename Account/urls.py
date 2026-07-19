from django.urls import path

from Account.views import (
    AdminUserUpdateView,
    LoginView,
    SignupView,
    SubUserListView,
    SubUserCreateView,
    SubUserUpdateView,
    logout_view,
    forgot_password,
)

urlpatterns = [
    path("edit-account/<uuid:pk>/", AdminUserUpdateView.as_view(), name="edit_account"),
    path("login/", LoginView.as_view(), name="login"),
    path("sign_up/", SignupView.as_view(), name="signup"),
    path("lost-password/", forgot_password, name="forgot_password"),
    path("dependents/", SubUserListView.as_view(), name="dependents_list"),
    path("dependents/add/", SubUserCreateView.as_view(), name="add_dependents"),
    path(
        "dependents/edit/<uuid:pk>/",
        SubUserUpdateView.as_view(),
        name="edit_dependents",
    ),
    path("logout/", logout_view, name="logout"),
]
