from django.urls import path
from .views import chat_room, inbox

urlpatterns = [
    path("inbox/", inbox, name="inbox"),
    path("<str:username>/", chat_room, name="chat_room"),
]