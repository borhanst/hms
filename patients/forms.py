from django import forms
from .models import Patient, VitalSign


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "first_name", "last_name", "date_of_birth", "age", "gender",
            "phone", "email", "address", "blood_group", "emergency_contact",
            "assigned_doctor", "allergies", "medical_history", "notes",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "age": forms.NumberInput(attrs={"class": "form-input"}),
            "gender": forms.Select(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "blood_group": forms.Select(attrs={"class": "form-input"}),
            "emergency_contact": forms.TextInput(attrs={"class": "form-input"}),
            "assigned_doctor": forms.Select(attrs={"class": "form-input"}),
            "allergies": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "medical_history": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }


class VitalSignForm(forms.ModelForm):
    class Meta:
        model = VitalSign
        fields = [
            "patient", "recorded_by", "blood_pressure_systolic", "blood_pressure_diastolic",
            "heart_rate", "temperature", "respiratory_rate", "oxygen_saturation",
            "weight", "height", "notes",
        ]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "recorded_by": forms.Select(attrs={"class": "form-input"}),
            "blood_pressure_systolic": forms.NumberInput(attrs={"class": "form-input", "placeholder": "120"}),
            "blood_pressure_diastolic": forms.NumberInput(attrs={"class": "form-input", "placeholder": "80"}),
            "heart_rate": forms.NumberInput(attrs={"class": "form-input", "placeholder": "72"}),
            "temperature": forms.NumberInput(attrs={"class": "form-input", "placeholder": "98.6", "step": "0.1"}),
            "respiratory_rate": forms.NumberInput(attrs={"class": "form-input", "placeholder": "16"}),
            "oxygen_saturation": forms.NumberInput(attrs={"class": "form-input", "placeholder": "98"}),
            "weight": forms.NumberInput(attrs={"class": "form-input", "placeholder": "70", "step": "0.01"}),
            "height": forms.NumberInput(attrs={"class": "form-input", "placeholder": "170", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
