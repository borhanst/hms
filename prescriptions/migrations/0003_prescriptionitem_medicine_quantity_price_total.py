from django.db import migrations, models
import django.db.models.deletion


def backfill_prescription_items(apps, schema_editor):
    PrescriptionItem = apps.get_model("prescriptions", "PrescriptionItem")
    Medicine = apps.get_model("pharmacy", "Medicine")
    db_alias = schema_editor.connection.alias

    for item in PrescriptionItem.objects.using(db_alias).select_related("prescription").filter(medicine__isnull=True).exclude(medicine_name=""):
        medicine = Medicine.objects.using(db_alias).filter(name__iexact=item.medicine_name).first()
        if not medicine:
            continue

        item.medicine_id = medicine.pk
        item.unit_price = medicine.unit_price
        item.total = item.quantity * medicine.unit_price
        item.save(update_fields=["medicine", "unit_price", "total"])


class Migration(migrations.Migration):

    dependencies = [
        ("prescriptions", "0002_prescription_status"),
        ("pharmacy", "0004_genericmedicine_brandmedicine"),
    ]

    operations = [
        migrations.AddField(
            model_name="prescriptionitem",
            name="medicine",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="prescription_items", to="pharmacy.medicine"),
        ),
        migrations.AddField(
            model_name="prescriptionitem",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="prescriptionitem",
            name="unit_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="prescriptionitem",
            name="total",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.RunPython(backfill_prescription_items, migrations.RunPython.noop),
    ]
