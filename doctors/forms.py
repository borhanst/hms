from django import forms
from .models import Doctor, DoctorSchedule
from core.models import User


class DoctorForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-input"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-input"}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"class": "form-input"}))
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-input"}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Leave blank to keep unchanged"}))

    class Meta:
        model = Doctor
        fields = ["specialization", "department", "phone", "bio", "is_available", "consultation_fee"]
        widgets = {
            "specialization": forms.TextInput(attrs={"class": "form-input"}),
            "department": forms.Select(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "bio": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "consultation_fee": forms.NumberInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email
            self.fields["username"].initial = self.instance.user.username
            self.fields["username"].widget.attrs["readonly"] = True
            self.fields["password"].required = False

    def save(self, commit=True):
        doctor = super().save(commit=False)
        if doctor.pk:
            user = doctor.user
        else:
            user = User(role=User.Role.DOCTOR)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data.get("email", "")
        user.username = self.cleaned_data["username"]
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        elif not user.pk:
            user.set_password("changeme123")
        if commit:
            user.save()
            doctor.user = user
            doctor.save()
        return doctor


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ["doctor", "day_of_week", "start_time", "end_time", "break_start", "break_end", "is_active", "max_patients"]
        widgets = {
            "doctor": forms.Select(attrs={"class": "form-input"}),
            "day_of_week": forms.Select(attrs={"class": "form-input"}),
            "start_time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "break_start": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "break_end": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "max_patients": forms.NumberInput(attrs={"class": "form-input"}),
        }
