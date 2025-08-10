from django.urls import path

from authentication import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path(
        "password-reset/done/",
        views.password_reset_done_view,
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.password_reset_complete_view,
        name="password_reset_complete",
    ),
]
