from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "start_time", "end_time", "status", "reason", "notes"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "doctor": forms.Select(attrs={"class": "form-input"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "reason": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
