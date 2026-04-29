from django.contrib.auth.decorators import login_required
from core.decorators import module_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
import json

from .models import Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemFormSet


@login_required
@module_required("billing")
def invoice_list(request):
    invoices = Invoice.objects.select_related("patient", "doctor__user").all()
    search = request.GET.get("search", "")
    status = request.GET.get("status", "")

    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search)
            | Q(patient__first_name__icontains=search)
            | Q(patient__last_name__icontains=search)
        )

    if status:
        invoices = invoices.filter(status=status)

    paginator = Paginator(invoices, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "invoices": page_obj,
        "search": search,
        "status": status,
        "status_choices": Invoice.STATUS_CHOICES,
    }

    if request.htmx:
        return render(request, "billing/partials/invoice_table.html", context)
    return render(request, "billing/invoice_list.html", context)


@login_required
@module_required("billing")
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related("patient", "doctor__user").prefetch_related("items"),
        pk=pk,
    )
    return render(request, "billing/invoice_detail.html", {"invoice": invoice})


@login_required
@module_required("billing")
def invoice_create(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            # Recalculate total
            invoice.save()
            messages.success(request, f"Invoice {invoice.invoice_number} created successfully.")
            return redirect("billing:invoice_detail", pk=invoice.pk)
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()
    return render(request, "billing/invoice_form.html", {
        "form": form,
        "formset": formset,
        "title": "New Invoice",
    })


@login_required
@module_required("billing")
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            invoice.save()
            messages.success(request, f"Invoice {invoice.invoice_number} updated successfully.")
            return redirect("billing:invoice_detail", pk=pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    return render(request, "billing/invoice_form.html", {
        "form": form,
        "formset": formset,
        "title": "Edit Invoice",
        "invoice": invoice,
    })


@login_required
@module_required("billing")
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        invoice.delete()
        messages.success(request, f"Invoice {invoice.invoice_number} deleted.")
        return redirect("billing:invoice_list")
    return render(request, "billing/invoice_confirm_delete.html", {"object": invoice})


@login_required
@module_required("billing")
def invoice_print(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related("patient", "doctor__user").prefetch_related("items"),
        pk=pk,
    )
    return render(request, "billing/invoice_print.html", {"invoice": invoice})


@login_required
@module_required("billing")
def billing_dashboard(request):
    """Billing overview for accountant/admin."""
    total_revenue = Invoice.objects.filter(status="PAID").aggregate(total=Sum("total"))["total"] or 0
    pending_revenue = Invoice.objects.filter(status__in=["SENT", "DRAFT"]).aggregate(total=Sum("total"))["total"] or 0
    total_invoices = Invoice.objects.count()
    paid_invoices = Invoice.objects.filter(status="PAID").count()
    overdue_invoices = Invoice.objects.filter(status="OVERDUE").count()

    recent_invoices = Invoice.objects.select_related("patient", "doctor__user").order_by("-created_at")[:10]

    # Revenue by month
    revenue_by_month = Invoice.objects.filter(status="PAID").annotate(
        month=TruncMonth("date")
    ).values("month").annotate(
        total=Sum("total")
    ).order_by("-month")[:6]
    revenue_by_month_list = [{"month": str(item["month"]), "total": float(item["total"])} for item in revenue_by_month]

    # By payment method
    by_payment = Invoice.objects.filter(payment_method__isnull=False).values(
        "payment_method"
    ).annotate(count=Count("id")).order_by("-count")
    payment_method_json = json.dumps(list(by_payment))

    context = {
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "overdue_invoices": overdue_invoices,
        "recent_invoices": recent_invoices,
        "revenue_by_month_json": json.dumps(revenue_by_month_list),
        "payment_method_json": payment_method_json,
    }
    return render(request, "billing/billing_dashboard.html", context)
