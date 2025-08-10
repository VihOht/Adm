from django.urls import path

from . import views

app_name = "agentAi"

urlpatterns = [
    path("", views.index, name="ai_test"),
    path("get_response/", views.get_response),
    path("get_messages/", views.get_conversation_messages, name="get_messages"),
]
