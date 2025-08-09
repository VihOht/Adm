from django.urls import path

from finance_statistics import views

urlpatterns = [path("", views.index, name="statistics")]
