from django.urls import path

from authentication import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile_view, name="edit_profile"),
    path(
        "profile/change-password/", views.change_password_view, name="change_password"
    ),
    path(
        "profile/delete-image/",
        views.delete_profile_image_view,
        name="delete_profile_image",
    ),
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
