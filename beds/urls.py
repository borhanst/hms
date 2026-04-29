from django.urls import path
from . import views

app_name = "beds"

urlpatterns = [
    path("", views.bed_dashboard, name="bed_dashboard"),
    path("wards/", views.ward_list, name="ward_list"),
    path("wards/create/", views.ward_create, name="ward_create"),
    path("wards/<int:pk>/edit/", views.ward_edit, name="ward_edit"),
    path("wards/<int:pk>/delete/", views.ward_delete, name="ward_delete"),
    path("beds/", views.bed_list, name="bed_list"),
    path("beds/create/", views.bed_create, name="bed_create"),
    path("beds/<int:pk>/edit/", views.bed_edit, name="bed_edit"),
    path("beds/<int:pk>/delete/", views.bed_delete, name="bed_delete"),
    path("admit/", views.admission_create, name="admission_create"),
    path("admissions/<int:pk>/discharge/", views.admission_discharge, name="admission_discharge"),
]
