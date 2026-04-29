from django.contrib import admin
from .models import NursingNote, MedicationAdministration


@admin.register(NursingNote)
class NursingNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "nurse", "priority", "created_at")
    list_filter = ("priority", "created_at")
    search_fields = ("title", "patient__first_name", "patient__last_name")


@admin.register(MedicationAdministration)
class MedicationAdministrationAdmin(admin.ModelAdmin):
    list_display = ("medicine_name", "patient", "nurse", "route", "administered_at")
    list_filter = ("route", "administered_at")
    search_fields = ("medicine_name", "patient__first_name", "patient__last_name")
