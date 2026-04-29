from django import forms
from .models import (
    DispensingRecord,
    Medicine,
    PharmacySale,
    PharmacySaleItem,
    Purchase,
    PurchaseItem,
    Supplier,
)


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ["name", "generic_name", "category", "manufacturer", "stock", "unit_price", "reorder_level", "expiry_date", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "generic_name": forms.TextInput(attrs={"class": "form-input"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "manufacturer": forms.TextInput(attrs={"class": "form-input"}),
            "stock": forms.NumberInput(attrs={"class": "form-input"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "reorder_level": forms.NumberInput(attrs={"class": "form-input"}),
            "expiry_date": forms.DateInput(format="%Y-%m-%d", attrs={"class": "form-input", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }


class DispensingForm(forms.ModelForm):
    class Meta:
        model = DispensingRecord
        fields = ["medicine", "prescription", "quantity", "dispensed_by", "notes"]
        widgets = {
            "medicine": forms.Select(attrs={"class": "form-input"}),
            "prescription": forms.Select(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "dispensed_by": forms.TextInput(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "contact_person", "phone", "email", "address", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "contact_person": forms.TextInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["supplier", "purchase_date", "reference_number", "status", "notes"]
        widgets = {
            "supplier": forms.Select(attrs={"class": "form-input"}),
            "purchase_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "reference_number": forms.TextInput(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ["medicine", "quantity", "unit_cost"]
        widgets = {
            "medicine": forms.Select(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "unit_cost": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
        }


PurchaseItemFormSet = forms.inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
)


class PharmacySaleForm(forms.ModelForm):
    class Meta:
        model = PharmacySale
        fields = ["patient", "prescription", "discount", "tax", "notes"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "prescription": forms.Select(attrs={"class": "form-input"}),
            "discount": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
            "tax": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class PharmacySaleItemForm(forms.ModelForm):
    class Meta:
        model = PharmacySaleItem
        fields = ["medicine", "quantity", "unit_price"]
        widgets = {
            "medicine": forms.Select(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        medicine = cleaned_data.get("medicine")
        if medicine and not cleaned_data.get("unit_price"):
            cleaned_data["unit_price"] = medicine.unit_price
        return cleaned_data


PharmacySaleItemFormSet = forms.inlineformset_factory(
    PharmacySale,
    PharmacySaleItem,
    form=PharmacySaleItemForm,
    extra=1,
    can_delete=True,
)
