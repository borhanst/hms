from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Q
from core.decorators import module_required

from .models import Ward, Bed, Admission
from .forms import WardForm, BedForm, AdmissionForm, DischargeForm


@login_required
@module_required("beds")
def bed_dashboard(request):
    total_beds = Bed.objects.count()
    available = Bed.objects.filter(status="AVAILABLE").count()
    occupied = Bed.objects.filter(status="OCCUPIED").count()
    maintenance = Bed.objects.filter(status="MAINTENANCE").count()
    active_admissions = Admission.objects.filter(discharged_at__isnull=True).select_related("patient", "bed__ward")[:10]
    wards = Ward.objects.annotate(bed_count=Count("beds"), occupied_count=Count("beds", filter=Q(beds__status="OCCUPIED")))

    context = {
        "total_beds": total_beds,
        "available": available,
        "occupied": occupied,
        "maintenance": maintenance,
        "active_admissions": active_admissions,
        "wards": wards,
    }
    return render(request, "beds/bed_dashboard.html", context)


@login_required
@module_required("beds")
def ward_list(request):
    wards = Ward.objects.annotate(bed_count=Count("beds"))
    paginator = Paginator(wards, 15)
    return render(request, "beds/ward_list.html", {"page_obj": paginator.get_page(request.GET.get("page")), "wards": paginator.get_page(request.GET.get("page"))})


@login_required
@module_required("beds")
def ward_create(request):
    if request.method == "POST":
        form = WardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ward created.")
            return redirect("beds:ward_list")
    else:
        form = WardForm()
    return render(request, "beds/ward_form.html", {"form": form, "title": "Add Ward"})


@login_required
@module_required("beds")
def ward_edit(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    if request.method == "POST":
        form = WardForm(request.POST, instance=ward)
        if form.is_valid():
            form.save()
            messages.success(request, "Ward updated.")
            return redirect("beds:ward_list")
    else:
        form = WardForm(instance=ward)
    return render(request, "beds/ward_form.html", {"form": form, "title": "Edit Ward"})


@login_required
@module_required("beds")
def ward_delete(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    if request.method == "POST":
        ward.delete()
        messages.success(request, "Ward deleted.")
        return redirect("beds:ward_list")
    return render(request, "beds/ward_confirm_delete.html", {"object": ward})


@login_required
@module_required("beds")
def bed_list(request):
    beds = Bed.objects.select_related("ward").all()
    ward_filter = request.GET.get("ward", "")
    status_filter = request.GET.get("status", "")
    if ward_filter:
        beds = beds.filter(ward_id=ward_filter)
    if status_filter:
        beds = beds.filter(status=status_filter)
    paginator = Paginator(beds, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "beds/bed_list.html", {
        "page_obj": page_obj,
        "beds": page_obj,
        "wards": Ward.objects.all(),
        "status_choices": Bed.STATUS_CHOICES,
    })


@login_required
@module_required("beds")
def bed_create(request):
    if request.method == "POST":
        form = BedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Bed added.")
            return redirect("beds:bed_list")
    else:
        form = BedForm()
    return render(request, "beds/bed_form.html", {"form": form, "title": "Add Bed"})


@login_required
@module_required("beds")
def bed_edit(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    if request.method == "POST":
        form = BedForm(request.POST, instance=bed)
        if form.is_valid():
            form.save()
            messages.success(request, "Bed updated.")
            return redirect("beds:bed_list")
    else:
        form = BedForm(instance=bed)
    return render(request, "beds/bed_form.html", {"form": form, "title": "Edit Bed"})


@login_required
@module_required("beds")
def bed_delete(request, pk):
    bed = get_object_or_404(Bed, pk=pk)
    if request.method == "POST":
        bed.delete()
        messages.success(request, "Bed deleted.")
        return redirect("beds:bed_list")
    return render(request, "beds/bed_confirm_delete.html", {"object": bed})


@login_required
@module_required("beds")
def admission_create(request):
    if request.method == "POST":
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            bed = admission.bed
            if bed.status != "AVAILABLE":
                messages.error(request, "Bed is not available.")
            else:
                bed.status = "OCCUPIED"
                bed.save()
                admission.save()
                messages.success(request, "Patient admitted.")
                return redirect("beds:bed_dashboard")
    else:
        form = AdmissionForm()
    return render(request, "beds/admission_form.html", {"form": form, "title": "Admit Patient"})


@login_required
@module_required("beds")
def admission_discharge(request, pk):
    admission = get_object_or_404(Admission.objects.select_related("bed"), pk=pk)
    if request.method == "POST":
        form = DischargeForm(request.POST, instance=admission)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.discharged_at = timezone.now()
            admission.save()
            admission.bed.status = "AVAILABLE"
            admission.bed.save()
            messages.success(request, "Patient discharged.")
            return redirect("beds:bed_dashboard")
    else:
        form = DischargeForm(instance=admission)
    return render(request, "beds/discharge_form.html", {"form": form, "admission": admission})
