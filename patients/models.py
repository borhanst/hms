from django.db import models
from doctors.models import Doctor


class Patient(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name="patients")
    allergies = models.TextField(blank=True, help_text="List known allergies, one per line")
    medical_history = models.TextField(blank=True, help_text="Past medical history, chronic conditions, surgeries")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ["-created_at"]


class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="vital_signs")
    recorded_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name="vital_records")
    blood_pressure_systolic = models.PositiveIntegerField(help_text="Systolic BP (mmHg)")
    blood_pressure_diastolic = models.PositiveIntegerField(help_text="Diastolic BP (mmHg)")
    heart_rate = models.PositiveIntegerField(help_text="Heart rate (bpm)")
    temperature = models.DecimalField(max_digits=4, decimal_places=1, help_text="Temperature (°F)")
    respiratory_rate = models.PositiveIntegerField(help_text="Respiratory rate (breaths/min)")
    oxygen_saturation = models.PositiveIntegerField(help_text="SpO2 (%)", null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight (kg)", null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height (cm)", null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

    @property
    def bp_display(self):
        return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"

    def __str__(self):
        return f"Vitals for {self.patient.full_name} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name_plural = "Vital Signs"
