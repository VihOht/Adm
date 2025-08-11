from django.urls import path

from . import views

app_name = "finance_statistics"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path(
        "ajax/day-transactions/",
        views.day_transactions_ajax,
        name="day_transactions_ajax",
    ),
]
