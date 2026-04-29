from django.contrib.auth.decorators import login_required
from core.decorators import admin_required, module_required, staff_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Patient, VitalSign
from .forms import PatientForm, VitalSignForm


@login_required
@module_required("patients")
def patient_list(request):
    patients = Patient.objects.select_related("assigned_doctor__user").all()
    search = request.GET.get("search", "")
    blood_group = request.GET.get("blood_group", "")

    if search:
        patients = patients.filter(
            first_name__icontains=search
        ) | patients.filter(
            last_name__icontains=search
        ) | patients.filter(
            phone__icontains=search
        )

    if blood_group:
        patients = patients.filter(blood_group=blood_group)

    # If doctor role, show only their patients
    if request.user.is_doctor:
        try:
            patients = patients.filter(assigned_doctor=request.user.doctor_profile)
        except Exception:
            patients = patients.none()

    paginator = Paginator(patients, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "patients": page_obj,
        "search": search,
        "blood_group": blood_group,
        "blood_groups": Patient.BLOOD_GROUP_CHOICES,
    }

    if request.htmx:
        return render(request, "patients/partials/patient_table.html", context)
    return render(request, "patients/patient_list.html", context)


@login_required
@module_required("patients")
def patient_detail(request, pk):
    patient = get_object_or_404(Patient.objects.select_related("assigned_doctor__user"), pk=pk)
    if request.user.is_doctor and patient.assigned_doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to access this patient.")
        return redirect("patients:patient_list")
    reports = patient.reports.select_related("doctor__user").all()[:10]
    prescriptions = patient.prescriptions.select_related("doctor__user").all()[:10]
    recent_vitals = patient.vital_signs.select_related("recorded_by__user").all()[:5]
    return render(request, "patients/patient_detail.html", {
        "patient": patient,
        "reports": reports,
        "prescriptions": prescriptions,
        "recent_vitals": recent_vitals,
    })


@login_required
@module_required("patients")
@staff_required
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient registered successfully.")
            return redirect("patients:patient_list")
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form, "title": "Register Patient"})


@login_required
@module_required("patients")
@staff_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.user.is_doctor and patient.assigned_doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to edit this patient.")
        return redirect("patients:patient_list")
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect("patients:patient_detail", pk=pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, "patients/patient_form.html", {"form": form, "title": "Edit Patient"})


@login_required
@module_required("patients")
@admin_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.user.is_doctor and patient.assigned_doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to delete this patient.")
        return redirect("patients:patient_list")
    if request.method == "POST":
        patient.delete()
        messages.success(request, "Patient deleted successfully.")
        if request.htmx:
            patients = Patient.objects.select_related("assigned_doctor__user").all()
            return render(request, "patients/partials/patient_table.html", {"patients": patients, "blood_groups": Patient.BLOOD_GROUP_CHOICES})
        return redirect("patients:patient_list")
    return render(request, "patients/patient_confirm_delete.html", {"patient": patient})


# --- Vital Signs ---

@login_required
@module_required("patients")
def vital_sign_list(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk)
    vitals = VitalSign.objects.select_related("recorded_by__user").filter(patient=patient)
    paginator = Paginator(vitals, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "patients/vital_sign_list.html", {
        "patient": patient,
        "page_obj": page_obj,
        "vitals": page_obj,
    })


@login_required
@module_required("patients")
def vital_sign_create(request, patient_pk):
    patient = get_object_or_404(Patient, pk=patient_pk)
    if request.method == "POST":
        form = VitalSignForm(request.POST)
        if form.is_valid():
            vital = form.save(commit=False)
            vital.patient = patient
            if request.user.is_doctor:
                vital.recorded_by = request.user.doctor_profile
            vital.save()
            messages.success(request, "Vital signs recorded successfully.")
            return redirect("patients:vital_sign_list", patient_pk=patient.pk)
    else:
        form = VitalSignForm(initial={"patient": patient})
        if request.user.is_doctor:
            try:
                form.fields["recorded_by"].initial = request.user.doctor_profile
            except Exception:
                pass
    return render(request, "patients/vital_sign_form.html", {
        "form": form,
        "patient": patient,
        "title": "Record Vital Signs",
    })


@login_required
@module_required("patients")
def vital_sign_edit(request, pk):
    vital = get_object_or_404(VitalSign, pk=pk)
    if request.user.is_doctor and vital.recorded_by != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to edit this vital sign record.")
        return redirect("patients:vital_sign_list", patient_pk=vital.patient.pk)
    if request.method == "POST":
        form = VitalSignForm(request.POST, instance=vital)
        if form.is_valid():
            form.save()
            messages.success(request, "Vital signs updated successfully.")
            return redirect("patients:vital_sign_list", patient_pk=vital.patient.pk)
    else:
        form = VitalSignForm(instance=vital)
    return render(request, "patients/vital_sign_form.html", {
        "form": form,
        "patient": vital.patient,
        "title": "Edit Vital Signs",
    })


@login_required
@module_required("patients")
def vital_sign_delete(request, pk):
    vital = get_object_or_404(VitalSign, pk=pk)
    if request.user.is_doctor and vital.recorded_by != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to delete this vital sign record.")
        return redirect("patients:vital_sign_list", patient_pk=vital.patient.pk)
    if request.method == "POST":
        patient_pk = vital.patient.pk
        vital.delete()
        messages.success(request, "Vital signs record deleted.")
        return redirect("patients:vital_sign_list", patient_pk=patient_pk)
    return render(request, "patients/vital_sign_confirm_delete.html", {"object": vital, "patient": vital.patient})
