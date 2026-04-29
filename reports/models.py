from django.db import models
from doctors.models import Doctor
from patients.models import Patient


class DiagnosticReport(models.Model):
    CATEGORY_CHOICES = [
        ("BLOOD", "Blood Test"),
        ("URINE", "Urine Test"),
        ("XRAY", "X-Ray"),
        ("MRI", "MRI"),
        ("CT", "CT Scan"),
        ("ULTRASOUND", "Ultrasound"),
        ("ECG", "ECG"),
        ("OTHER", "Other"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="reports")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name="reports")
    test_name = models.CharField(max_length=200)
    test_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="OTHER")
    result = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    notes = models.TextField(blank=True)
    file = models.FileField(upload_to="reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_name} - {self.patient.full_name}"

    class Meta:
        ordering = ["-created_at"]
