from django.db import models
from django.conf import settings


class Doctor(models.Model):
    DEPARTMENT_CHOICES = [
        ("GENERAL", "General Medicine"),
        ("CARDIOLOGY", "Cardiology"),
        ("NEUROLOGY", "Neurology"),
        ("ORTHOPEDICS", "Orthopedics"),
        ("PEDIATRICS", "Pediatrics"),
        ("DERMATOLOGY", "Dermatology"),
        ("ENT", "ENT"),
        ("OPHTHALMOLOGY", "Ophthalmology"),
        ("GYNECOLOGY", "Gynecology"),
        ("RADIOLOGY", "Radiology"),
        ("PATHOLOGY", "Pathology"),
        ("OTHER", "Other"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    specialization = models.CharField(max_length=100)
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES, default="GENERAL")
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.specialization}"

    class Meta:
        ordering = ["-created_at"]


class DoctorSchedule(models.Model):
    DAY_CHOICES = [
        ("MON", "Monday"),
        ("TUE", "Tuesday"),
        ("WED", "Wednesday"),
        ("THU", "Thursday"),
        ("FRI", "Friday"),
        ("SAT", "Saturday"),
        ("SUN", "Sunday"),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField(help_text="Consultation start time")
    end_time = models.TimeField(help_text="Consultation end time")
    break_start = models.TimeField(null=True, blank=True, help_text="Break start time (optional)")
    break_end = models.TimeField(null=True, blank=True, help_text="Break end time (optional)")
    is_active = models.BooleanField(default=True, help_text="Uncheck to disable this schedule")
    max_patients = models.PositiveIntegerField(default=20, help_text="Maximum patients per day (0 = unlimited)")

    class Meta:
        ordering = ["doctor", "day_of_week"]
        verbose_name_plural = "Doctor Schedules"
        unique_together = ["doctor", "day_of_week"]

    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"

    @property
    def has_break(self):
        return bool(self.break_start and self.break_end)
