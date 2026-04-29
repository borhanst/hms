from django.urls import path
from . import views

app_name = "prescriptions"

urlpatterns = [
    path("", views.prescription_list, name="prescription_list"),
    path("create/", views.prescription_create, name="prescription_create"),
    path("medicine-search/", views.medicine_search, name="medicine_search"),
    path("<int:pk>/", views.prescription_detail, name="prescription_detail"),
    path("<int:pk>/edit/", views.prescription_edit, name="prescription_edit"),
    path("<int:pk>/delete/", views.prescription_delete, name="prescription_delete"),
    path("<int:pk>/print/", views.prescription_print, name="prescription_print"),
]
