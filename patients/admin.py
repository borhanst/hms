from django.contrib import admin
from .models import Patient, VitalSign


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "gender", "phone", "blood_group", "assigned_doctor", "created_at")
    list_filter = ("gender", "blood_group")
    search_fields = ("first_name", "last_name", "phone")


@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ("patient", "bp_display", "heart_rate", "temperature", "recorded_at")
    list_filter = ("recorded_at",)
    search_fields = ("patient__first_name", "patient__last_name")
    date_hierarchy = "recorded_at"
