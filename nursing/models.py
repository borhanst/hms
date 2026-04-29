from django.db import models
from patients.models import Patient
from doctors.models import Doctor
from core.models import User


class NursingNote(models.Model):
    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="nursing_notes")
    nurse = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={"role": "NURSE"}, related_name="nursing_notes")
    title = models.CharField(max_length=200)
    note = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"


class MedicationAdministration(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medication_administrations")
    nurse = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={"role": "NURSE"}, related_name="medication_administrations")
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    route = models.CharField(max_length=50, choices=[
        ("ORAL", "Oral"), ("IV", "Intravenous"), ("IM", "Intramuscular"),
        ("SC", "Subcutaneous"), ("TOPICAL", "Topical"), ("RECTAL", "Rectal"),
        ("INHALATION", "Inhalation"), ("SUBLINGUAL", "Sublingual"),
    ], default="ORAL")
    administered_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-administered_at"]

    def __str__(self):
        return f"{self.medicine_name} {self.dosage} - {self.patient.full_name}"
