import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("patients", "0002_patient_allergies_patient_medical_history_vitalsign"),
        ("pharmacy", "0001_initial"),
        ("prescriptions", "0002_prescription_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True)),
                ("contact_person", models.CharField(blank=True, max_length=150)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("movement_type", models.CharField(choices=[("PURCHASE", "Purchase"), ("SALE", "Sale"), ("ADJUSTMENT", "Adjustment")], max_length=20)),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("reference", models.CharField(blank=True, max_length=100)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("medicine", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stock_movements", to="pharmacy.medicine")),
                ("performed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pharmacy_stock_movements", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Purchase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("purchase_date", models.DateField(default=django.utils.timezone.now)),
                ("reference_number", models.CharField(blank=True, max_length=50)),
                ("status", models.CharField(choices=[("DRAFT", "Draft"), ("COMPLETED", "Completed"), ("CANCELLED", "Cancelled")], default="DRAFT", max_length=20)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("supplier", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchases", to="pharmacy.supplier")),
            ],
            options={"ordering": ["-purchase_date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="PurchaseItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField()),
                ("unit_cost", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, editable=False, max_digits=12)),
                ("medicine", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_items", to="pharmacy.medicine")),
                ("purchase", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="pharmacy.purchase")),
            ],
        ),
        migrations.CreateModel(
            name="PharmacySale",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sale_date", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("DRAFT", "Draft"), ("COMPLETED", "Completed"), ("CANCELLED", "Cancelled")], default="DRAFT", max_length=20)),
                ("subtotal", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("discount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("tax", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invoice", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pharmacy_sale", to="billing.invoice")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pharmacy_sales", to="patients.patient")),
                ("prescription", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pharmacy_sales", to="prescriptions.prescription")),
                ("sold_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="pharmacy_sales", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-sale_date"]},
        ),
        migrations.CreateModel(
            name="PharmacySaleItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total", models.DecimalField(decimal_places=2, editable=False, max_digits=12)),
                ("medicine", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sale_items", to="pharmacy.medicine")),
                ("sale", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="pharmacy.pharmacysale")),
            ],
        ),
    ]
