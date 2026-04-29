from django import forms
from .models import NursingNote, MedicationAdministration


class NursingNoteForm(forms.ModelForm):
    class Meta:
        model = NursingNote
        fields = ["patient", "title", "note", "priority"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "note": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "priority": forms.Select(attrs={"class": "form-input"}),
        }


class MedicationAdministrationForm(forms.ModelForm):
    class Meta:
        model = MedicationAdministration
        fields = ["patient", "medicine_name", "dosage", "route", "scheduled_time", "notes"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "medicine_name": forms.TextInput(attrs={"class": "form-input"}),
            "dosage": forms.TextInput(attrs={"class": "form-input"}),
            "route": forms.Select(attrs={"class": "form-input"}),
            "scheduled_time": forms.DateTimeInput(attrs={"class": "form-input", "type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
