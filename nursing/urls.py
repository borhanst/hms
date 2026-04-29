from django.urls import path
from . import views

app_name = "nursing"

urlpatterns = [
    path("", views.nursing_dashboard, name="nursing_dashboard"),
    path("notes/", views.note_list, name="note_list"),
    path("notes/create/", views.note_create, name="note_create"),
    path("notes/<int:pk>/edit/", views.note_edit, name="note_edit"),
    path("notes/<int:pk>/delete/", views.note_delete, name="note_delete"),
    path("medications/", views.medication_list, name="medication_list"),
    path("medications/create/", views.medication_create, name="medication_create"),
]
