from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pharmacy", "0002_supplier_stockmovement_purchase_pharmacysale"),
    ]

    operations = [
        migrations.AddField(
            model_name="medicine",
            name="expiry_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
