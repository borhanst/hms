from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "patient", "doctor", "date", "total", "status", "payment_method")
    list_filter = ("status", "payment_method")
    search_fields = ("invoice_number", "patient__first_name", "patient__last_name")
    date_hierarchy = "date"
    inlines = [InvoiceItemInline]
