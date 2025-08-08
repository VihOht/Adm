from django.urls import path

from landingpage import views

urlpatterns = [
    path("", views.index, name="landingpage"),
    path("test-messages/", views.test_messages, name="test_messages"),
]
