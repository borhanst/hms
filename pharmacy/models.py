from django.db import models
from django.conf import settings
from django.db import transaction
from django.utils import timezone


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ("TABLET", "Tablet"),
        ("CAPSULE", "Capsule"),
        ("SYRUP", "Syrup"),
        ("INJECTION", "Injection"),
        ("CREAM", "Cream"),
        ("DROPS", "Drops"),
        ("INHALER", "Inhaler"),
        ("SUPPOSITORY", "Suppository"),
        ("OTHER", "Other"),
    ]

    name = models.CharField(max_length=200, unique=True)
    generic_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="TABLET")
    manufacturer = models.CharField(max_length=200, blank=True)
    stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.PositiveIntegerField(default=10, help_text="Alert when stock falls below this")
    expiry_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()}) - Stock: {self.stock}"

    @property
    def is_low_stock(self):
        return self.stock <= self.reorder_level

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days

    @property
    def is_expired(self):
        return self.expiry_date is not None and self.expiry_date < timezone.localdate()

    @property
    def is_near_expiry(self):
        days = self.days_until_expiry
        return days is not None and 0 <= days <= 30


class DispensingRecord(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="dispensings")
    prescription = models.ForeignKey("prescriptions.Prescription", on_delete=models.SET_NULL, null=True, blank=True, related_name="dispensings")
    quantity = models.PositiveIntegerField()
    dispensed_at = models.DateTimeField(auto_now_add=True)
    dispensed_by = models.CharField(max_length=100, blank=True, help_text="Staff name")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-dispensed_at"]

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity} - {self.dispensed_at.strftime('%Y-%m-%d %H:%M')}"


class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("PURCHASE", "Purchase"),
        ("SALE", "Sale"),
        ("ADJUSTMENT", "Adjustment"),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name="stock_movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="pharmacy_stock_movements")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.medicine.name} x{self.quantity}"


class Purchase(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchases")
    purchase_date = models.DateField(default=timezone.now)
    reference_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-purchase_date", "-created_at"]

    def __str__(self):
        return f"Purchase #{self.pk or 'new'} - {self.supplier.name}"

    def recalculate_total(self):
        self.total = sum(item.total for item in self.items.all())
        return self.total

    def complete(self, received_by=None):
        if self.status == "COMPLETED":
            return

        with transaction.atomic():
            self.recalculate_total()
            for item in self.items.select_related("medicine"):
                medicine = item.medicine
                medicine.stock += item.quantity
                medicine.save(update_fields=["stock", "updated_at"])
                StockMovement.objects.create(
                    medicine=medicine,
                    movement_type="PURCHASE",
                    quantity=item.quantity,
                    unit_price=item.unit_cost,
                    reference=self.reference_number or f"Purchase #{self.pk}",
                    performed_by=received_by,
                    notes=self.notes,
                )
            self.status = "COMPLETED"
            self.save(update_fields=["status", "total", "updated_at"])


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name="purchase_items")
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity}"


class PharmacySale(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="pharmacy_sales")
    prescription = models.ForeignKey("prescriptions.Prescription", on_delete=models.SET_NULL, null=True, blank=True, related_name="pharmacy_sales")
    invoice = models.OneToOneField("billing.Invoice", on_delete=models.SET_NULL, null=True, blank=True, related_name="pharmacy_sale")
    sold_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="pharmacy_sales")
    sale_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-sale_date"]

    def __str__(self):
        return f"Pharmacy sale #{self.pk or 'new'} - {self.patient.full_name}"

    def recalculate_total(self):
        self.subtotal = sum(item.total for item in self.items.all())
        self.total = self.subtotal - self.discount + self.tax
        return self.total

    def complete(self):
        if self.status == "COMPLETED" and self.invoice:
            return self.invoice

        from billing.models import Invoice, InvoiceItem

        with transaction.atomic():
            items = list(self.items.select_related("medicine"))
            if not items:
                raise ValueError("Sale must include at least one medicine.")
            for item in items:
                if item.medicine.stock < item.quantity:
                    raise ValueError(f"Insufficient stock for {item.medicine.name}.")
                if item.medicine.is_expired:
                    raise ValueError(f"{item.medicine.name} is expired and cannot be sold.")

            self.recalculate_total()
            invoice = self.invoice or Invoice.objects.create(
                patient=self.patient,
                doctor=self.prescription.doctor if self.prescription else None,
                status="DRAFT",
                discount=self.discount,
                tax=self.tax,
                notes=self.notes,
            )

            if self.invoice:
                invoice.items.all().delete()
                invoice.discount = self.discount
                invoice.tax = self.tax
                invoice.notes = self.notes
                invoice.save()

            for item in items:
                medicine = item.medicine
                medicine.stock -= item.quantity
                medicine.save(update_fields=["stock", "updated_at"])
                StockMovement.objects.create(
                    medicine=medicine,
                    movement_type="SALE",
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    reference=f"Sale #{self.pk}",
                    performed_by=self.sold_by,
                    notes=self.notes,
                )
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=medicine.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )

            invoice.save()
            self.invoice = invoice
            self.status = "COMPLETED"
            self.save(update_fields=["invoice", "status", "subtotal", "total", "updated_at"])
            return invoice


class PharmacySaleItem(models.Model):
    sale = models.ForeignKey(PharmacySale, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.medicine.unit_price
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.medicine.name} x{self.quantity}"




# apps/medicines/models.py

from django.db import models


class GenericMedicine(models.Model):
    name = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    brand_names_url = models.URLField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Generic Medicine"
        verbose_name_plural = "Generic Medicines"

    def __str__(self):
        return self.name


class BrandMedicine(models.Model):
    generic = models.ForeignKey(
        GenericMedicine,
        on_delete=models.CASCADE,
        related_name="brands",
        null=True,
        blank=True,
    )

    brand_name = models.CharField(max_length=500)
    dosage_form = models.CharField(max_length=255, blank=True)
    strength = models.TextField(blank=True)
    company = models.CharField(max_length=500, blank=True)
    pack_size_price = models.TextField(blank=True)

    brand_detail_url = models.URLField(unique=True)
    source_url = models.URLField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Brand Medicine"
        verbose_name_plural = "Brand Medicines"

    def __str__(self):
        return self.brand_name