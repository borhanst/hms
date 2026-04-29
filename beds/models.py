from django.db import models
from patients.models import Patient
from doctors.models import Doctor


class Ward(models.Model):
    WARD_TYPES = [
        ("GENERAL", "General Ward"),
        ("SEMI_PRIVATE", "Semi-Private"),
        ("PRIVATE", "Private"),
        ("ICU", "ICU"),
        ("CCU", "CCU"),
        ("PEDIATRIC", "Pediatric"),
        ("MATERNITY", "Maternity"),
        ("ISOLATION", "Isolation"),
    ]

    name = models.CharField(max_length=100)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPES)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_ward_type_display()})"


class Bed(models.Model):
    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("OCCUPIED", "Occupied"),
        ("MAINTENANCE", "Maintenance"),
    ]

    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name="beds")
    bed_number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="AVAILABLE")

    class Meta:
        ordering = ["ward", "bed_number"]
        unique_together = ["ward", "bed_number"]

    def __str__(self):
        return f"Bed {self.bed_number} - {self.ward.name} ({self.get_status_display()})"


class Admission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="admissions")
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name="admissions")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name="admissions")
    diagnosis = models.TextField()
    admitted_at = models.DateTimeField(auto_now_add=True)
    discharged_at = models.DateTimeField(null=True, blank=True)
    discharge_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-admitted_at"]

    def __str__(self):
        return f"{self.patient.full_name} - Bed {self.bed.bed_number} ({self.admitted_at.strftime('%Y-%m-%d')})"

    @property
    def is_active(self):
        return self.discharged_at is None

    @property
    def days_stayed(self):
        from django.utils import timezone
        end = self.discharged_at or timezone.now()
        return (end - self.admitted_at).days
