from django import forms
from .models import Invoice, InvoiceItem


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["patient", "doctor", "due_date", "status", "payment_method", "discount", "tax", "notes"]
        widgets = {
            "patient": forms.Select(attrs={"class": "form-input"}),
            "doctor": forms.Select(attrs={"class": "form-input"}),
            "due_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "payment_method": forms.Select(attrs={"class": "form-input"}),
            "discount": forms.NumberInput(attrs={"class": "form-input"}),
            "tax": forms.NumberInput(attrs={"class": "form-input"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 2}),
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["description", "quantity", "unit_price"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-input"}),
            "quantity": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
        }


InvoiceItemFormSet = forms.inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True,
)
