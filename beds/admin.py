from django.contrib import admin
from .models import Ward, Bed, Admission


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ("name", "ward_type", "price_per_day")
    list_filter = ("ward_type",)


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("bed_number", "ward", "status")
    list_filter = ("status", "ward")


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ("patient", "bed", "doctor", "admitted_at", "discharged_at")
    list_filter = ("admitted_at",)
    search_fields = ("patient__first_name", "patient__last_name")
