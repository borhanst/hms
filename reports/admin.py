from django.contrib import admin
from .models import DiagnosticReport


@admin.register(DiagnosticReport)
class DiagnosticReportAdmin(admin.ModelAdmin):
    list_display = ("test_name", "patient", "doctor", "test_category", "status", "created_at")
    list_filter = ("status", "test_category")
    search_fields = ("test_name", "patient__first_name", "patient__last_name")
