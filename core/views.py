from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json

from .forms import LoginForm, UserCreateForm, UserUpdateForm
from .models import User
from .decorators import admin_required
from doctors.models import Doctor
from patients.models import Patient
from reports.models import DiagnosticReport
from prescriptions.models import Prescription


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect("core:dashboard")
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("core:login")


@login_required
def dashboard_view(request):
    if request.user.is_doctor:
        try:
            doctor = request.user.doctor_profile
            context = {
                "my_patients": Patient.objects.filter(assigned_doctor=doctor).count(),
                "my_reports": DiagnosticReport.objects.filter(doctor=doctor).count(),
                "my_prescriptions": Prescription.objects.filter(doctor=doctor).count(),
                "recent_patients": Patient.objects.filter(assigned_doctor=doctor).order_by("-created_at")[:5],
                "recent_reports": DiagnosticReport.objects.filter(doctor=doctor).order_by("-created_at")[:5],
                "pending_reports": DiagnosticReport.objects.filter(doctor=doctor, status="PENDING").count(),
            }
        except Doctor.DoesNotExist:
            context = {"recent_patients": [], "recent_reports": [], "pending_reports": 0}
    else:
        context = {
            "total_doctors": Doctor.objects.count(),
            "total_patients": Patient.objects.count(),
            "total_reports": DiagnosticReport.objects.count(),
            "total_prescriptions": Prescription.objects.count(),
            "recent_patients": Patient.objects.order_by("-created_at")[:5],
            "recent_reports": DiagnosticReport.objects.order_by("-created_at")[:5],
            "pending_reports": DiagnosticReport.objects.filter(status="PENDING").count(),
        }

    # Chart data for non-doctor users
    if not request.user.is_doctor:
        # Patients registered per month (last 6 months)
        patient_trend = Patient.objects.annotate(
            month=TruncMonth("created_at")
        ).values("month").annotate(
            count=Count("id")
        ).order_by("-month")[:6]
        # Convert date objects to strings for JSON serialization
        patient_trend_list = [{"month": str(item["month"]), "count": item["count"]} for item in patient_trend]
        context["patient_trend_json"] = json.dumps(patient_trend_list)

        # Reports by category
        reports_by_category = DiagnosticReport.objects.values(
            "test_category"
        ).annotate(
            count=Count("id")
        ).order_by("-count")
        context["reports_by_category_json"] = json.dumps(list(reports_by_category))

        # Prescriptions by status
        rx_by_status = Prescription.objects.values("status").annotate(
            count=Count("id")
        ).order_by("-count")
        context["rx_by_status_json"] = json.dumps(list(rx_by_status))

    return render(request, "core/dashboard.html", context)


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("core:profile")
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, "core/profile.html", {"form": form})


# --- User Management (Admin Only) ---
@login_required
@admin_required
def user_list_view(request):
    users = User.objects.all().order_by("-date_joined")
    search = request.GET.get("search", "")
    if search:
        users = users.filter(username__icontains=search) | users.filter(
            first_name__icontains=search
        ) | users.filter(last_name__icontains=search)

    if request.htmx:
        return render(request, "core/partials/user_table.html", {"users": users})
    return render(request, "core/user_list.html", {"users": users, "search": search})


@login_required
@admin_required
def user_create_view(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User '{user.username}' created successfully.")
            if request.htmx:
                return render(request, "core/partials/user_table.html", {"users": User.objects.all().order_by("-date_joined")})
            return redirect("core:user_list")
    else:
        form = UserCreateForm()

    template = "core/partials/user_form.html" if request.htmx else "core/user_form.html"
    return render(request, template, {"form": form, "title": "Create User"})


@login_required
@admin_required
def user_update_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect("core:user_list")
    else:
        form = UserUpdateForm(instance=user)
    return render(request, "core/user_form.html", {"form": form, "title": "Edit User"})


@login_required
@admin_required
def user_delete_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted.")
        if request.htmx:
            return render(request, "core/partials/user_table.html", {"users": User.objects.all().order_by("-date_joined")})
        return redirect("core:user_list")
    return render(request, "core/user_confirm_delete.html", {"object": user, "type": "User"})
