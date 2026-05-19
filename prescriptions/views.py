from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from core.decorators import module_required
from core.permissions import can_access_module

from pharmacy.models import Medicine

from .models import Prescription
from .forms import PrescriptionForm, PrescriptionItemFormSet


@login_required
@module_required("prescriptions")
def prescription_list(request):
    prescriptions = Prescription.objects.select_related("patient", "doctor__user").all()
    search = request.GET.get("search", "")

    if search:
        prescriptions = prescriptions.filter(
            patient__first_name__icontains=search
        ) | prescriptions.filter(
            patient__last_name__icontains=search
        ) | prescriptions.filter(
            diagnosis__icontains=search
        )

    if request.user.is_doctor:
        try:
            prescriptions = prescriptions.filter(doctor=request.user.doctor_profile)
        except Exception:
            prescriptions = prescriptions.none()

    paginator = Paginator(prescriptions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "prescriptions": page_obj,
        "search": search,
    }

    if request.htmx:
        return render(request, "prescriptions/partials/prescription_table.html", context)
    return render(request, "prescriptions/prescription_list.html", context)


@login_required
@module_required("prescriptions")
def prescription_detail(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related("patient", "doctor__user").prefetch_related("items"),
        pk=pk,
    )
    if request.user.is_doctor and prescription.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to view this prescription.")
        return redirect("prescriptions:prescription_list")
    return render(request, "prescriptions/prescription_detail.html", {
        "prescription": prescription,
        "can_create_pharmacy_sale": can_access_module(request.user, "pharmacy"),
    })


@login_required
@module_required("prescriptions")
def prescription_create(request):
    if getattr(request.user, "is_receptionist", False):
        messages.error(request, "Receptionists cannot create prescriptions.")
        return redirect("prescriptions:prescription_list")
    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            prescription = form.save()
            formset.instance = prescription
            formset.save()
            messages.success(request, "Prescription created successfully.")
            return redirect("prescriptions:prescription_detail", pk=prescription.pk)
    else:
        form = PrescriptionForm()
        formset = PrescriptionItemFormSet()
    return render(request, "prescriptions/prescription_form.html", {
        "form": form,
        "formset": formset,
        "title": "Create Prescription",
    })


@login_required
@module_required("prescriptions")
def prescription_edit(request, pk):
    if getattr(request.user, "is_receptionist", False):
        messages.error(request, "Receptionists cannot edit prescriptions.")
        return redirect("prescriptions:prescription_list")
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.user.is_doctor and prescription.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to edit this prescription.")
        return redirect("prescriptions:prescription_list")
    if request.method == "POST":
        form = PrescriptionForm(request.POST, instance=prescription)
        formset = PrescriptionItemFormSet(request.POST, instance=prescription)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Prescription updated successfully.")
            return redirect("prescriptions:prescription_detail", pk=pk)
    else:
        form = PrescriptionForm(instance=prescription)
        formset = PrescriptionItemFormSet(instance=prescription)
    return render(request, "prescriptions/prescription_form.html", {
        "form": form,
        "formset": formset,
        "title": "Edit Prescription",
    })


@login_required
@module_required("prescriptions")
def prescription_delete(request, pk):
    if getattr(request.user, "is_receptionist", False) or getattr(request.user, "is_doctor", False):
        messages.error(request, "Only admins can delete prescriptions.")
        return redirect("prescriptions:prescription_list")
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.user.is_doctor and prescription.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to delete this prescription.")
        return redirect("prescriptions:prescription_list")
    if request.method == "POST":
        prescription.delete()
        messages.success(request, "Prescription deleted successfully.")
        if request.htmx:
            prescriptions = Prescription.objects.select_related("patient", "doctor__user").all()
            return render(request, "prescriptions/partials/prescription_table.html", {"prescriptions": prescriptions})
        return redirect("prescriptions:prescription_list")
    return render(request, "prescriptions/prescription_confirm_delete.html", {"prescription": prescription})


@login_required
@module_required("prescriptions")
def prescription_print(request, pk):
    prescription = get_object_or_404(
        Prescription.objects.select_related("patient", "doctor__user").prefetch_related("items"),
        pk=pk,
    )
    if request.user.is_doctor and prescription.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to access this prescription.")
        return redirect("prescriptions:prescription_list")
    return render(request, "prescriptions/prescription_print.html", {"prescription": prescription})


@login_required
@module_required("prescriptions")
def medicine_search(request):
    query = (request.GET.get("q") or "").strip()
    medicines = Medicine.objects.all().order_by("name")

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query)
            | Q(generic_name__icontains=query)
            | Q(manufacturer__icontains=query)
        )

    results = [
        {
            "id": medicine.pk,
            "name": medicine.name,
            "generic_name": medicine.generic_name,
            "manufacturer": medicine.manufacturer,
            "unit_price": str(medicine.unit_price),
        }
        for medicine in medicines[:10]
    ]
    return JsonResponse(results, safe=False)
