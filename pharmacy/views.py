from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import DecimalField, ExpressionWrapper, F, Q, Sum
from django.utils import timezone
from core.decorators import module_required
from prescriptions.models import Prescription

from .models import (
    DispensingRecord,
    Medicine,
    PharmacySale,
    Purchase,
    StockMovement,
    Supplier,
)
from .forms import (
    DispensingForm,
    MedicineForm,
    PharmacySaleForm,
    PharmacySaleItemFormSet,
    PurchaseForm,
    PurchaseItemFormSet,
    SupplierForm,
)


@login_required
@module_required("pharmacy")
def medicine_list(request):
    medicines = Medicine.objects.all()
    search = request.GET.get("search", "")
    category = request.GET.get("category", "")
    low_stock = request.GET.get("low_stock", "")
    expiry_status = request.GET.get("expiry_status", "")
    today = timezone.localdate()
    near_expiry_limit = today + timezone.timedelta(days=30)

    if search:
        medicines = medicines.filter(Q(name__icontains=search) | Q(generic_name__icontains=search))
    if category:
        medicines = medicines.filter(category=category)
    if low_stock:
        medicines = medicines.filter(stock__lte=F("reorder_level"))
    if expiry_status == "expired":
        medicines = medicines.filter(expiry_date__lt=today)
    elif expiry_status == "near_expiry":
        medicines = medicines.filter(expiry_date__gte=today, expiry_date__lte=near_expiry_limit)

    paginator = Paginator(medicines, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "medicines": page_obj,
        "search": search,
        "category": category,
        "expiry_status": expiry_status,
        "category_choices": Medicine.CATEGORY_CHOICES,
        "low_stock_count": Medicine.objects.filter(stock__lte=F("reorder_level")).count(),
        "expired_count": Medicine.objects.filter(expiry_date__lt=today).count(),
        "near_expiry_count": Medicine.objects.filter(expiry_date__gte=today, expiry_date__lte=near_expiry_limit).count(),
    }
    if request.htmx:
        return render(request, "pharmacy/partials/medicine_table.html", context)
    return render(request, "pharmacy/medicine_list.html", context)


@login_required
@module_required("pharmacy")
def medicine_create(request):
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine added successfully.")
            return redirect("pharmacy:medicine_list")
    else:
        form = MedicineForm()
    return render(request, "pharmacy/medicine_form.html", {"form": form, "title": "Add Medicine"})


@login_required
@module_required("pharmacy")
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine updated successfully.")
            return redirect("pharmacy:medicine_list")
    else:
        form = MedicineForm(instance=medicine)
    return render(request, "pharmacy/medicine_form.html", {"form": form, "title": "Edit Medicine"})


@login_required
@module_required("pharmacy")
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        medicine.delete()
        messages.success(request, "Medicine deleted.")
        return redirect("pharmacy:medicine_list")
    return render(request, "pharmacy/medicine_confirm_delete.html", {"object": medicine})


@login_required
@module_required("pharmacy")
def medicine_dispose_expired(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == "POST":
        if not medicine.is_expired:
            messages.error(request, f"{medicine.name} is not expired.")
        elif medicine.stock == 0:
            messages.info(request, f"{medicine.name} has no stock to dispose.")
        else:
            disposed_quantity = medicine.stock
            medicine.stock = 0
            medicine.save(update_fields=["stock", "updated_at"])
            StockMovement.objects.create(
                medicine=medicine,
                movement_type="ADJUSTMENT",
                quantity=disposed_quantity,
                unit_price=medicine.unit_price,
                reference=f"Expired medicine #{medicine.pk}",
                performed_by=request.user,
                notes="Expired stock disposed",
            )
            messages.success(request, f"Disposed {disposed_quantity} units of expired {medicine.name}.")
    return redirect("pharmacy:medicine_list")


@login_required
@module_required("pharmacy")
def dispensing_create(request):
    if request.method == "POST":
        form = DispensingForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            medicine = record.medicine
            if medicine.stock < record.quantity:
                messages.error(request, f"Insufficient stock. Available: {medicine.stock}")
            elif medicine.is_expired:
                messages.error(request, f"{medicine.name} is expired and cannot be dispensed.")
            else:
                medicine.stock -= record.quantity
                medicine.save()
                record.save()
                messages.success(request, f"Dispensed {record.quantity} x {medicine.name}")
                return redirect("pharmacy:dispensing_list")
    else:
        form = DispensingForm()
    return render(request, "pharmacy/dispensing_form.html", {"form": form, "title": "Dispense Medicine"})


@login_required
@module_required("pharmacy")
def dispensing_list(request):
    records = DispensingRecord.objects.select_related("medicine", "prescription").all()
    paginator = Paginator(records, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "pharmacy/dispensing_list.html", {
        "page_obj": page_obj,
        "records": page_obj,
    })


@login_required
@module_required("pharmacy")
def supplier_list(request):
    suppliers = Supplier.objects.all()
    search = request.GET.get("search", "")
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search)
            | Q(contact_person__icontains=search)
            | Q(phone__icontains=search)
        )
    paginator = Paginator(suppliers, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "pharmacy/supplier_list.html", {"suppliers": page_obj, "page_obj": page_obj, "search": search})


@login_required
@module_required("pharmacy")
def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier added successfully.")
            return redirect("pharmacy:supplier_list")
    else:
        form = SupplierForm()
    return render(request, "pharmacy/supplier_form.html", {"form": form, "title": "Add Supplier"})


@login_required
@module_required("pharmacy")
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect("pharmacy:supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "pharmacy/supplier_form.html", {"form": form, "title": "Edit Supplier"})


@login_required
@module_required("pharmacy")
def purchase_list(request):
    purchases = Purchase.objects.select_related("supplier").prefetch_related("items").all()
    status = request.GET.get("status", "")
    if status:
        purchases = purchases.filter(status=status)
    paginator = Paginator(purchases, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "pharmacy/purchase_list.html", {
        "purchases": page_obj,
        "page_obj": page_obj,
        "status": status,
        "status_choices": Purchase.STATUS_CHOICES,
    })


@login_required
@module_required("pharmacy")
def purchase_create(request):
    if request.method == "POST":
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            purchase = form.save()
            formset.instance = purchase
            formset.save()
            purchase.recalculate_total()
            purchase.save(update_fields=["total", "updated_at"])
            if purchase.status == "COMPLETED":
                purchase.status = "DRAFT"
                purchase.save(update_fields=["status", "updated_at"])
                purchase.complete(received_by=request.user)
            messages.success(request, "Purchase saved successfully.")
            return redirect("pharmacy:purchase_list")
    else:
        form = PurchaseForm()
        formset = PurchaseItemFormSet()
    return render(request, "pharmacy/purchase_form.html", {"form": form, "formset": formset, "title": "New Purchase"})


@login_required
@module_required("pharmacy")
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase.objects.select_related("supplier").prefetch_related("items__medicine"), pk=pk)
    return render(request, "pharmacy/purchase_detail.html", {"purchase": purchase})


@login_required
@module_required("pharmacy")
def purchase_complete(request, pk):
    purchase = get_object_or_404(Purchase.objects.prefetch_related("items__medicine"), pk=pk)
    if request.method == "POST":
        purchase.complete(received_by=request.user)
        messages.success(request, "Purchase completed and stock updated.")
    return redirect("pharmacy:purchase_detail", pk=pk)


@login_required
@module_required("pharmacy")
def sale_list(request):
    sales = PharmacySale.objects.select_related("patient", "invoice").prefetch_related("items__medicine").all()
    status = request.GET.get("status", "")
    if status:
        sales = sales.filter(status=status)
    paginator = Paginator(sales, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "pharmacy/sale_list.html", {
        "sales": page_obj,
        "page_obj": page_obj,
        "status": status,
        "status_choices": PharmacySale.STATUS_CHOICES,
    })


@login_required
@module_required("pharmacy")
def sale_create(request):
    prescription = None
    prescription_id = request.GET.get("from_prescription") or request.POST.get("prescription")
    if prescription_id:
        prescription = get_object_or_404(
            Prescription.objects.select_related("patient", "doctor").prefetch_related("items__medicine"),
            pk=prescription_id,
        )

    if request.method == "POST":
        form = PharmacySaleForm(request.POST)
        formset = PharmacySaleItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            sale = form.save(commit=False)
            sale.sold_by = request.user
            sale.save()
            formset.instance = sale
            formset.save()
            try:
                invoice = sale.complete()
            except ValueError as exc:
                messages.error(request, str(exc))
            else:
                messages.success(request, f"Sale completed and invoice {invoice.invoice_number} created.")
                return redirect("pharmacy:sale_detail", pk=sale.pk)
    else:
        form_initial = {}
        formset_initial = None
        if prescription:
            form_initial = {
                "patient": prescription.patient,
                "prescription": prescription,
            }
            formset_initial = [
                {
                    "medicine": item.medicine,
                    "quantity": item.quantity,
                    "unit_price": item.display_unit_price,
                }
                for item in prescription.items.all()
                if item.medicine_id
            ]
        form = PharmacySaleForm(initial=form_initial)
        formset = PharmacySaleItemFormSet(initial=formset_initial)
    return render(request, "pharmacy/sale_form.html", {
        "form": form,
        "formset": formset,
        "prescription": prescription,
        "title": "New Pharmacy Sale",
    })


@login_required
@module_required("pharmacy")
def sale_detail(request, pk):
    sale = get_object_or_404(PharmacySale.objects.select_related("patient", "invoice").prefetch_related("items__medicine"), pk=pk)
    return render(request, "pharmacy/sale_detail.html", {"sale": sale})


@login_required
@module_required("pharmacy")
def stock_movement_list(request):
    movements = StockMovement.objects.select_related("medicine", "performed_by").all()
    movement_type = request.GET.get("movement_type", "")
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    paginator = Paginator(movements, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "pharmacy/stock_movement_list.html", {
        "movements": page_obj,
        "page_obj": page_obj,
        "movement_type": movement_type,
        "movement_types": StockMovement.MOVEMENT_TYPES,
    })


@login_required
@module_required("pharmacy")
def pharmacy_reports(request):
    today = timezone.localdate()
    near_expiry_limit = today + timezone.timedelta(days=30)
    revenue_expression = ExpressionWrapper(
        F("quantity") * F("unit_price"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    top_sold = StockMovement.objects.filter(movement_type="SALE").annotate(
        line_total=revenue_expression
    ).values(
        "medicine__name"
    ).annotate(quantity=Sum("quantity"), revenue=Sum("line_total")).order_by("-quantity")[:20]
    low_stock = Medicine.objects.filter(stock__lte=F("reorder_level")).order_by("stock")[:30]
    expired_medicines = Medicine.objects.filter(expiry_date__lt=today).order_by("expiry_date", "name")[:30]
    near_expiry_medicines = Medicine.objects.filter(expiry_date__gte=today, expiry_date__lte=near_expiry_limit).order_by("expiry_date", "name")[:30]
    purchase_total = Purchase.objects.filter(status="COMPLETED").aggregate(total=Sum("total"))["total"] or 0
    sales_total = PharmacySale.objects.filter(status="COMPLETED").aggregate(total=Sum("total"))["total"] or 0
    return render(request, "pharmacy/pharmacy_reports.html", {
        "top_sold": top_sold,
        "low_stock": low_stock,
        "expired_medicines": expired_medicines,
        "near_expiry_medicines": near_expiry_medicines,
        "purchase_total": purchase_total,
        "sales_total": sales_total,
    })


@login_required
@module_required("pharmacy")
def pharmacy_dashboard(request):
    today = timezone.localdate()
    near_expiry_limit = today + timezone.timedelta(days=30)
    total_medicines = Medicine.objects.count()
    low_stock = Medicine.objects.filter(stock__lte=F("reorder_level")).count()
    expired_count = Medicine.objects.filter(expiry_date__lt=today).count()
    near_expiry_count = Medicine.objects.filter(expiry_date__gte=today, expiry_date__lte=near_expiry_limit).count()
    total_value = Medicine.objects.aggregate(total=Sum(F("stock") * F("unit_price")))["total"] or 0
    today_dispensed = DispensingRecord.objects.filter(dispensed_at__date=timezone.now().date()).count()
    today_sales = PharmacySale.objects.filter(sale_date__date=timezone.now().date(), status="COMPLETED")
    today_revenue = today_sales.aggregate(total=Sum("total"))["total"] or 0
    today_purchases = Purchase.objects.filter(purchase_date=timezone.now().date()).count()

    low_stock_medicines = Medicine.objects.filter(stock__lte=F("reorder_level")).order_by("stock")[:10]
    expired_medicines = Medicine.objects.filter(expiry_date__lt=today).order_by("expiry_date", "name")[:10]
    near_expiry_medicines = Medicine.objects.filter(expiry_date__gte=today, expiry_date__lte=near_expiry_limit).order_by("expiry_date", "name")[:10]
    recent_dispensing = DispensingRecord.objects.select_related("medicine").all()[:10]
    recent_sales = PharmacySale.objects.select_related("patient", "invoice").all()[:10]
    recent_purchases = Purchase.objects.select_related("supplier").all()[:10]
    recent_movements = StockMovement.objects.select_related("medicine").all()[:10]

    context = {
        "total_medicines": total_medicines,
        "low_stock": low_stock,
        "expired_count": expired_count,
        "near_expiry_count": near_expiry_count,
        "total_value": total_value,
        "today_dispensed": today_dispensed,
        "today_revenue": today_revenue,
        "today_sales": today_sales.count(),
        "today_purchases": today_purchases,
        "low_stock_medicines": low_stock_medicines,
        "expired_medicines": expired_medicines,
        "near_expiry_medicines": near_expiry_medicines,
        "recent_dispensing": recent_dispensing,
        "recent_sales": recent_sales,
        "recent_purchases": recent_purchases,
        "recent_movements": recent_movements,
    }
    return render(request, "pharmacy/pharmacy_dashboard.html", context)
