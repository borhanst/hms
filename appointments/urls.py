from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("", views.appointment_list, name="appointment_list"),
    path("create/", views.appointment_create, name="appointment_create"),
    path("calendar/", views.appointment_calendar, name="appointment_calendar"),
    path("<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("<int:pk>/edit/", views.appointment_edit, name="appointment_edit"),
    path("<int:pk>/delete/", views.appointment_delete, name="appointment_delete"),
    # Doctor-specific appointments
    path("doctor/<int:doctor_pk>/", views.doctor_appointments, name="doctor_appointments"),
]
