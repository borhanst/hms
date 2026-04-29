from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from core.decorators import module_required

from .models import DiagnosticReport
from .forms import ReportForm


@login_required
@module_required("reports")
def report_list(request):
    reports = DiagnosticReport.objects.select_related("patient", "doctor__user").all()
    search = request.GET.get("search", "")
    status = request.GET.get("status", "")
    category = request.GET.get("category", "")

    if search:
        reports = reports.filter(
            test_name__icontains=search
        ) | reports.filter(
            patient__first_name__icontains=search
        ) | reports.filter(
            patient__last_name__icontains=search
        )

    if status:
        reports = reports.filter(status=status)

    if category:
        reports = reports.filter(test_category=category)

    if request.user.is_doctor:
        try:
            reports = reports.filter(doctor=request.user.doctor_profile)
        except Exception:
            reports = reports.none()

    paginator = Paginator(reports, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "reports": page_obj,
        "search": search,
        "status": status,
        "category": category,
        "status_choices": DiagnosticReport.STATUS_CHOICES,
        "category_choices": DiagnosticReport.CATEGORY_CHOICES,
    }

    if request.htmx:
        return render(request, "reports/partials/report_table.html", context)
    return render(request, "reports/report_list.html", context)


@login_required
@module_required("reports")
def report_detail(request, pk):
    report = get_object_or_404(DiagnosticReport.objects.select_related("patient", "doctor__user"), pk=pk)
    if request.user.is_doctor and report.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to view this report.")
        return redirect("reports:report_list")
    return render(request, "reports/report_detail.html", {"report": report})


@login_required
@module_required("reports")
def report_create(request):
    if not (request.user.is_admin or request.user.is_doctor or request.user.is_laboratorian):
        messages.error(request, "You do not have permission to create reports.")
        return redirect("reports:report_list")
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Report created successfully.")
            return redirect("reports:report_list")
    else:
        form = ReportForm()
    return render(request, "reports/report_form.html", {"form": form, "title": "Create Report"})


@login_required
@module_required("reports")
def report_edit(request, pk):
    if not (request.user.is_admin or request.user.is_doctor or request.user.is_laboratorian):
        messages.error(request, "You do not have permission to edit reports.")
        return redirect("reports:report_list")
    report = get_object_or_404(DiagnosticReport, pk=pk)
    if request.user.is_doctor and report.doctor != getattr(request.user, "doctor_profile", None):
        messages.error(request, "You do not have permission to edit this report.")
        return redirect("reports:report_list")
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, "Report updated successfully.")
            return redirect("reports:report_detail", pk=pk)
    else:
        form = ReportForm(instance=report)
    return render(request, "reports/report_form.html", {"form": form, "title": "Edit Report"})


@login_required
@module_required("reports")
def report_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, "Only admins can delete reports.")
        return redirect("reports:report_list")
    report = get_object_or_404(DiagnosticReport, pk=pk)
    if request.method == "POST":
        report.delete()
        messages.success(request, "Report deleted successfully.")
        if request.htmx:
            reports = DiagnosticReport.objects.select_related("patient", "doctor__user").all()
            return render(request, "reports/partials/report_table.html", {"reports": reports})
        return redirect("reports:report_list")
    return render(request, "reports/report_confirm_delete.html", {"report": report})
