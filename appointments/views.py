from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import date, timedelta
from core.decorators import module_required

from .models import Appointment
from .forms import AppointmentForm
from doctors.models import Doctor
from patients.models import Patient


def _check_conflict(doctor, appointment_date, start_time, end_time, exclude_pk=None):
    """Check if there's a scheduling conflict for a doctor at the given time."""
    qs = Appointment.objects.filter(
        doctor=doctor,
        date=appointment_date,
        status__in=["SCHEDULED", "IN_PROGRESS"],
    ).exclude(pk=exclude_pk)

    for appt in qs:
        # Check time overlap
        if start_time < appt.end_time and end_time > appt.start_time:
            return appt
    return None


@login_required
@module_required("appointments")
def appointment_list(request):
    appointments = Appointment.objects.select_related("patient", "doctor__user").all()
    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    appt_date = request.GET.get("date", "")

    if search:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search)
            | Q(patient__last_name__icontains=search)
            | Q(doctor__user__first_name__icontains=search)
            | Q(doctor__user__last_name__icontains=search)
        )

    if status:
        appointments = appointments.filter(status=status)

    if appt_date:
        appointments = appointments.filter(date=appt_date)

    # If doctor role, show only their appointments
    if request.user.is_doctor:
        try:
            appointments = appointments.filter(doctor=request.user.doctor_profile)
        except Exception:
            appointments = appointments.none()

    paginator = Paginator(appointments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "appointments": page_obj,
        "search": search,
        "status": status,
        "appt_date": appt_date,
        "status_choices": Appointment.STATUS_CHOICES,
    }

    if request.htmx:
        return render(request, "appointments/partials/appointment_table.html", context)
    return render(request, "appointments/appointment_list.html", context)


@login_required
@module_required("appointments")
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related("patient", "doctor__user", "created_by"),
        pk=pk,
    )
    if request.user.is_doctor and appointment.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to view this appointment.")
        return redirect("appointments:appointment_list")
    return render(request, "appointments/appointment_detail.html", {"appointment": appointment})


@login_required
@module_required("appointments")
def appointment_create(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            # Check for conflicts
            conflict = _check_conflict(
                appt.doctor, appt.date, appt.start_time, appt.end_time
            )
            if conflict:
                messages.error(
                    request,
                    f"Conflict: Doctor already has an appointment from {conflict.start_time} to {conflict.end_time} with {conflict.patient.full_name}.",
                )
            else:
                appt.created_by = request.user
                appt.save()
                messages.success(request, "Appointment created successfully.")
                return redirect("appointments:appointment_list")
    else:
        form = AppointmentForm()
        # Pre-fill doctor if user is a doctor
        if request.user.is_doctor:
            try:
                form.fields["doctor"].initial = request.user.doctor_profile
                form.fields["doctor"].widget.attrs["readonly"] = True
            except Exception:
                pass

    return render(request, "appointments/appointment_form.html", {
        "form": form,
        "title": "New Appointment",
    })


@login_required
@module_required("appointments")
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user.is_doctor and appointment.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to edit this appointment.")
        return redirect("appointments:appointment_list")

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appt = form.save(commit=False)
            # Check for conflicts
            conflict = _check_conflict(
                appt.doctor, appt.date, appt.start_time, appt.end_time, exclude_pk=appt.pk
            )
            if conflict:
                messages.error(
                    request,
                    f"Conflict: Doctor already has an appointment from {conflict.start_time} to {conflict.end_time} with {conflict.patient.full_name}.",
                )
            else:
                form.save()
                messages.success(request, "Appointment updated successfully.")
                return redirect("appointments:appointment_detail", pk=pk)
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "appointments/appointment_form.html", {
        "form": form,
        "title": "Edit Appointment",
        "appointment": appointment,
    })


@login_required
@module_required("appointments")
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user.is_doctor and appointment.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to delete this appointment.")
        return redirect("appointments:appointment_list")

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted.")
        if request.htmx:
            appointments = Appointment.objects.select_related("patient", "doctor__user").all()
            return render(request, "appointments/partials/appointment_table.html", {
                "appointments": appointments,
                "status_choices": Appointment.STATUS_CHOICES,
            })
        return redirect("appointments:appointment_list")
    return render(request, "appointments/appointment_confirm_delete.html", {"object": appointment})


@login_required
@module_required("appointments")
def appointment_calendar(request):
    """Daily and weekly calendar views."""
    calendar_mode = request.GET.get("mode", "day")
    if calendar_mode not in {"day", "week"}:
        calendar_mode = "day"

    def parse_date(value, fallback):
        if value:
            try:
                return date.fromisoformat(value)
            except ValueError:
                return fallback
        return fallback

    selected_date = parse_date(request.GET.get("date"), date.today())
    week_seed = parse_date(request.GET.get("week_start"), selected_date)
    start_date = week_seed - timedelta(days=week_seed.weekday())
    end_date = start_date + timedelta(days=6)

    appointments = Appointment.objects.select_related("patient", "doctor__user").order_by("date", "start_time")

    if request.user.is_doctor:
        try:
            appointments = appointments.filter(doctor=request.user.doctor_profile)
        except Exception:
            appointments = appointments.none()

    day_appointments = appointments.filter(date=selected_date).order_by("start_time")
    week_appointments = appointments.filter(date__range=[start_date, end_date]).order_by("date", "start_time")

    appointments_by_date = {}
    current = start_date
    while current <= end_date:
        appointments_by_date[current] = []
        current += timedelta(days=1)

    for appt in week_appointments:
        appointments_by_date.setdefault(appt.date, []).append(appt)

    context = {
        "calendar_mode": calendar_mode,
        "selected_date": selected_date,
        "previous_day": selected_date - timedelta(days=1),
        "next_day": selected_date + timedelta(days=1),
        "day_appointments": day_appointments,
        "start_date": start_date,
        "end_date": end_date,
        "previous_week_start": start_date - timedelta(days=7),
        "next_week_start": start_date + timedelta(days=7),
        "appointments_by_date": appointments_by_date,
        "week_range": [(start_date + timedelta(days=i)) for i in range(7)],
        "today": date.today(),
    }
    return render(request, "appointments/appointment_calendar.html", context)


@login_required
@module_required("appointments")
def doctor_appointments(request, doctor_pk):
    """View all appointments for a specific doctor."""
    doctor = get_object_or_404(Doctor.objects.select_related("user"), pk=doctor_pk)
    appointments = Appointment.objects.select_related("patient").filter(doctor=doctor).order_by("-date", "-start_time")
    paginator = Paginator(appointments, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "appointments/doctor_appointments.html", {
        "doctor": doctor,
        "page_obj": page_obj,
        "appointments": page_obj,
    })
