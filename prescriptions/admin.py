from django.contrib import admin
from .models import Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "diagnosis", "follow_up_date", "created_at")
    list_filter = ("created_at",)
    search_fields = ("patient__first_name", "patient__last_name", "diagnosis")
    inlines = [PrescriptionItemInline]
