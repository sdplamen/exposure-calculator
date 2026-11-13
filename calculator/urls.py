from django.urls import path
from . import views

app_name = "calculator"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("api/exposure/", views.api_exposure, name="api_exposure"),
]