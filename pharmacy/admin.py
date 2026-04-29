from django.contrib import admin
from .models import (
    DispensingRecord,
    Medicine,
    PharmacySale,
    PharmacySaleItem,
    Purchase,
    PurchaseItem,
    StockMovement,
    Supplier,
)
from .models import GenericMedicine, BrandMedicine


@admin.register(GenericMedicine)
class GenericMedicineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url", "brand_names_url", "updated_at")
    search_fields = ("name", "url")


@admin.register(BrandMedicine)
class BrandMedicineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "brand_name",
        "dosage_form",
        "company",
        "generic",
        "updated_at",
    )
    search_fields = (
        "brand_name",
        "company",
        "strength",
        "brand_detail_url",
        "generic__name",
    )
    list_filter = ("dosage_form", "company")


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "stock", "unit_price", "reorder_level", "expiry_date", "is_low_stock", "is_expired")
    list_filter = ("category", "expiry_date")
    search_fields = ("name", "generic_name", "manufacturer")


@admin.register(DispensingRecord)
class DispensingRecordAdmin(admin.ModelAdmin):
    list_display = ("medicine", "quantity", "prescription", "dispensed_by", "dispensed_at")
    list_filter = ("dispensed_at",)
    search_fields = ("medicine__name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_person", "phone", "email")


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "supplier", "purchase_date", "reference_number", "status", "total")
    list_filter = ("status", "purchase_date")
    search_fields = ("supplier__name", "reference_number")
    inlines = [PurchaseItemInline]


class PharmacySaleItemInline(admin.TabularInline):
    model = PharmacySaleItem
    extra = 1


@admin.register(PharmacySale)
class PharmacySaleAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "sale_date", "status", "total", "invoice")
    list_filter = ("status", "sale_date")
    search_fields = ("patient__first_name", "patient__last_name", "invoice__invoice_number")
    inlines = [PharmacySaleItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("medicine", "movement_type", "quantity", "unit_price", "reference", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("medicine__name", "reference")
