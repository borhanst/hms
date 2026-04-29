from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path("", views.patient_list, name="patient_list"),
    path("create/", views.patient_create, name="patient_create"),
    path("<int:pk>/", views.patient_detail, name="patient_detail"),
    path("<int:pk>/edit/", views.patient_edit, name="patient_edit"),
    path("<int:pk>/delete/", views.patient_delete, name="patient_delete"),
    # Vital Signs
    path("<int:patient_pk>/vitals/", views.vital_sign_list, name="vital_sign_list"),
    path("<int:patient_pk>/vitals/create/", views.vital_sign_create, name="vital_sign_create"),
    path("vitals/<int:pk>/edit/", views.vital_sign_edit, name="vital_sign_edit"),
    path("vitals/<int:pk>/delete/", views.vital_sign_delete, name="vital_sign_delete"),
]
