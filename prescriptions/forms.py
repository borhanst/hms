from django import forms
from pharmacy.models import Medicine
from .models import Prescription, PrescriptionItem


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["patient", "doctor", "diagnosis", "status", "notes", "follow_up_date"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "doctor": forms.Select(attrs={"class": "form-input"}),
            "diagnosis": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
            "follow_up_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
        }


class PrescriptionItemForm(forms.ModelForm):
    medicine_search = forms.CharField(
        required=False,
        label="Medicine",
        widget=forms.TextInput(
            attrs={
                "class": "form-input medicine-search",
                "placeholder": "Search medicine...",
                "autocomplete": "off",
                "data-role": "medicine-search",
            }
        ),
    )

    class Meta:
        model = PrescriptionItem
        fields = ["medicine", "dosage", "quantity", "unit_price", "frequency", "duration", "instructions"]
        widgets = {
            "medicine": forms.HiddenInput(attrs={"data-role": "medicine-id"}),
            "dosage": forms.TextInput(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": "1", "data-role": "medicine-quantity"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "readonly": "readonly", "data-role": "medicine-unit-price"}),
            "frequency": forms.Select(attrs={"class": "form-input"}),
            "duration": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. 7 days"}),
            "instructions": forms.TextInput(attrs={"class": "form-input", "placeholder": "After meals, etc."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["medicine"].queryset = Medicine.objects.order_by("name")
        self.fields["quantity"].required = False
        self.fields["unit_price"].required = False
        self.fields["quantity"].initial = self.fields["quantity"].initial or 1
        self.fields["quantity"].widget.attrs.setdefault("value", 1)

        instance = kwargs.get("instance") or self.instance
        if instance and getattr(instance, "pk", None):
            self.fields["medicine_search"].initial = instance.display_medicine_name
            self.fields["quantity"].initial = instance.quantity or 1
            self.fields["quantity"].widget.attrs["value"] = instance.quantity or 1
            self.fields["unit_price"].initial = instance.display_unit_price
        else:
            self.fields["quantity"].initial = 1
            self.fields["quantity"].widget.attrs["value"] = 1

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get("medicine")
        medicine_search = (cleaned_data.get("medicine_search") or "").strip()

        if medicine:
            cleaned_data["unit_price"] = medicine.unit_price
        elif medicine_search:
            matched = Medicine.objects.filter(name__iexact=medicine_search).first()
            if matched:
                cleaned_data["medicine"] = matched
                cleaned_data["unit_price"] = matched.unit_price

        if not cleaned_data.get("medicine") and self.instance.pk is None:
            meaningful_fields = [
                cleaned_data.get("dosage"),
                cleaned_data.get("quantity"),
                cleaned_data.get("frequency"),
                cleaned_data.get("duration"),
                cleaned_data.get("instructions"),
                medicine_search,
            ]
            if any(meaningful_fields):
                raise forms.ValidationError({"medicine_search": "Select a medicine from the suggestions."})

        return cleaned_data

    def has_changed(self):
        changed = super().has_changed()
        if not changed:
            return False

        medicine = self.data.get(self.add_prefix("medicine"))
        if medicine:
            return True

        relevant_keys = ("dosage", "frequency", "duration", "instructions", "medicine_search")
        if any((self.data.get(self.add_prefix(key)) or "").strip() for key in relevant_keys):
            return True

        return False


PrescriptionItemFormSet = forms.inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True,
)
