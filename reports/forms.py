from django import forms
from .models import DiagnosticReport


class ReportForm(forms.ModelForm):
    class Meta:
        model = DiagnosticReport
        fields = ["patient", "doctor", "test_name", "test_category", "result", "status", "notes", "file"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "doctor": forms.Select(attrs={"class": "form-input"}),
            "test_name": forms.TextInput(attrs={"class": "form-input"}),
            "test_category": forms.Select(attrs={"class": "form-input"}),
            "result": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "file": forms.ClearableFileInput(attrs={"class": "form-input"}),
        }
