from django import forms
from .models import Ward, Bed, Admission


class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ["name", "ward_type", "price_per_day", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "ward_type": forms.Select(attrs={"class": "form-input"}),
            "price_per_day": forms.NumberInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class BedForm(forms.ModelForm):
    class Meta:
        model = Bed
        fields = ["ward", "bed_number", "status"]
        widgets = {
            "ward": forms.Select(attrs={"class": "form-input"}),
            "bed_number": forms.TextInput(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
        }


class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ["patient", "bed", "doctor", "diagnosis"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "bed": forms.Select(attrs={"class": "form-input"}),
            "doctor": forms.Select(attrs={"class": "form-input"}),
            "diagnosis": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class DischargeForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ["discharge_notes"]
        widgets = {
            "discharge_notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }
