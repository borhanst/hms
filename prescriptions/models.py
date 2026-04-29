from django.db import models
from doctors.models import Doctor
from patients.models import Patient
from pharmacy.models import Medicine


class Prescription(models.Model):
    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("DISCONTINUED", "Discontinued"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name="prescriptions")
    diagnosis = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rx for {self.patient.full_name} by Dr. {self.doctor}"

    class Meta:
        ordering = ["-created_at"]


class PrescriptionItem(models.Model):
    FREQUENCY_CHOICES = [
        ("OD", "Once Daily"),
        ("BD", "Twice Daily"),
        ("TDS", "Three Times Daily"),
        ("QDS", "Four Times Daily"),
        ("SOS", "As Needed"),
        ("STAT", "Immediately"),
    ]

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True, related_name="prescription_items")
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="OD")
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.display_medicine_name} - {self.dosage}"

    @property
    def display_medicine_name(self):
        return self.medicine.name if self.medicine else self.medicine_name

    @property
    def display_unit_price(self):
        if self.medicine:
            return self.medicine.unit_price
        return self.unit_price

    def save(self, *args, **kwargs):
        if self.medicine:
            self.medicine_name = self.medicine.name
            self.unit_price = self.medicine.unit_price
        if not self.quantity:
            self.quantity = 1
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
