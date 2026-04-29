from django import forms
from .models import EmployeeProfile, Attendance, LeaveRequest


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ["employee_id", "department", "designation", "join_date", "salary", "phone", "address", "emergency_contact"]
        widgets = {
            "employee_id": forms.TextInput(attrs={"class": "form-input"}),
            "department": forms.TextInput(attrs={"class": "form-input"}),
            "designation": forms.TextInput(attrs={"class": "form-input"}),
            "join_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "salary": forms.NumberInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "emergency_contact": forms.TextInput(attrs={"class": "form-input"}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["employee", "date", "check_in", "check_out", "status", "notes"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-input"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "check_in": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "check_out": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "leave_type": forms.Select(attrs={"class": "form-input"}),
            "start_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "reason": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }


class LeaveReviewForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["status", "review_notes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-input"}),
            "review_notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }
