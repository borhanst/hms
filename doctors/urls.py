from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),
    path("create/", views.doctor_create, name="doctor_create"),
    path("<int:pk>/", views.doctor_detail, name="doctor_detail"),
    path("<int:pk>/edit/", views.doctor_edit, name="doctor_edit"),
    path("<int:pk>/delete/", views.doctor_delete, name="doctor_delete"),
    # Doctor Schedule
    path("<int:doctor_pk>/schedule/", views.doctor_schedule_list, name="doctor_schedule_list"),
    path("<int:doctor_pk>/schedule/create/", views.doctor_schedule_create, name="doctor_schedule_create"),
    path("schedule/<int:pk>/edit/", views.doctor_schedule_edit, name="doctor_schedule_edit"),
    path("schedule/<int:pk>/delete/", views.doctor_schedule_delete, name="doctor_schedule_delete"),
]
