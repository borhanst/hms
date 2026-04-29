from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from core.decorators import module_required

from .models import Doctor, DoctorSchedule
from .forms import DoctorForm, DoctorScheduleForm


@login_required
@module_required("doctors")
def doctor_list(request):
    doctors = Doctor.objects.select_related("user").all()
    search = request.GET.get("search", "")
    department = request.GET.get("department", "")

    if search:
        doctors = doctors.filter(
            user__first_name__icontains=search
        ) | doctors.filter(
            user__last_name__icontains=search
        ) | doctors.filter(
            specialization__icontains=search
        )

    if department:
        doctors = doctors.filter(department=department)

    paginator = Paginator(doctors, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "doctors": page_obj,
        "search": search,
        "department": department,
        "departments": Doctor.DEPARTMENT_CHOICES,
    }

    if request.htmx:
        return render(request, "doctors/partials/doctor_table.html", context)
    return render(request, "doctors/doctor_list.html", context)


@login_required
@module_required("doctors")
def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related("user"), pk=pk)
    return render(request, "doctors/doctor_detail.html", {"doctor": doctor})


@login_required
@module_required("doctors")
def doctor_create(request):
    if not (request.user.is_admin or request.user.is_superuser):
        messages.error(request, "Only admins can add doctors.")
        return redirect("doctors:doctor_list")

    if request.method == "POST":
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor added successfully.")
            return redirect("doctors:doctor_list")
    else:
        form = DoctorForm()

    return render(request, "doctors/doctor_form.html", {"form": form, "title": "Add Doctor"})


@login_required
@module_required("doctors")
def doctor_edit(request, pk):
    if not (request.user.is_admin or request.user.is_superuser):
        messages.error(request, "Only admins can edit doctors.")
        return redirect("doctors:doctor_list")

    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == "POST":
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor updated successfully.")
            return redirect("doctors:doctor_detail", pk=pk)
    else:
        form = DoctorForm(instance=doctor)

    return render(request, "doctors/doctor_form.html", {"form": form, "title": "Edit Doctor"})


@login_required
@module_required("doctors")
def doctor_delete(request, pk):
    if not (request.user.is_admin or request.user.is_superuser):
        messages.error(request, "Only admins can delete doctors.")
        return redirect("doctors:doctor_list")

    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == "POST":
        doctor.user.delete()
        messages.success(request, "Doctor deleted successfully.")
        if request.htmx:
            doctors = Doctor.objects.select_related("user").all()
            return render(request, "doctors/partials/doctor_table.html", {"doctors": doctors, "departments": Doctor.DEPARTMENT_CHOICES})
        return redirect("doctors:doctor_list")
    return render(request, "doctors/doctor_confirm_delete.html", {"doctor": doctor})


# --- Doctor Schedule ---

@login_required
@module_required("doctors")
def doctor_schedule_list(request, doctor_pk):
    doctor = get_object_or_404(Doctor.objects.select_related("user"), pk=doctor_pk)
    schedules = DoctorSchedule.objects.select_related("doctor").filter(doctor=doctor)
    return render(request, "doctors/doctor_schedule_list.html", {
        "doctor": doctor,
        "schedules": schedules,
    })


@login_required
@module_required("doctors")
def doctor_schedule_create(request, doctor_pk):
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    if not (request.user.is_admin or request.user.is_superuser):
        messages.error(request, "Only admins can manage doctor schedules.")
        return redirect("doctors:doctor_detail", pk=doctor.pk)
    if request.method == "POST":
        form = DoctorScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Schedule added successfully.")
            return redirect("doctors:doctor_schedule_list", doctor_pk=doctor.pk)
    else:
        form = DoctorScheduleForm(initial={"doctor": doctor})
    return render(request, "doctors/doctor_schedule_form.html", {
        "form": form,
        "doctor": doctor,
        "title": "Add Schedule",
    })


@login_required
@module_required("doctors")
def doctor_schedule_edit(request, pk):
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    if not (request.user.is_admin or request.user.is_superuser):
        messages.error(request, "Only admins can manage doctor schedules.")
        return redirect("doctors:doctor_schedule_list", doctor_pk=schedule.doctor.pk)
    if request.method == "POST":
        form = DoctorScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Schedule updated successfully.")
            return redirect("doctors:doctor_schedule_list", doctor_pk=schedule.doctor.pk)
    else:
        form = DoctorScheduleForm(instance=schedule)
    return render(request, "doctors/doctor_schedule_form.html", {
        "form": form,
        "doctor": schedule.doctor,
        "title": "Edit Schedule",
    })


@login_required
@module_required("doctors")
def doctor_schedule_delete(request, pk):
    schedule = get_object_or_404(DoctorSchedule, pk=pk)
    if not (request.user.is_admin or request.user.is_superuser):
        messages.error(request, "Only admins can manage doctor schedules.")
        return redirect("doctors:doctor_schedule_list", doctor_pk=schedule.doctor.pk)
    if request.method == "POST":
        doctor_pk = schedule.doctor.pk
        schedule.delete()
        messages.success(request, "Schedule deleted.")
        return redirect("doctors:doctor_schedule_list", doctor_pk=doctor_pk)
    return render(request, "doctors/doctor_schedule_confirm_delete.html", {
        "object": schedule,
        "doctor": schedule.doctor,
    })
