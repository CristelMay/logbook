from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("lobby/", views.lobby_dashboard, name="lobby_dashboard"),
]
