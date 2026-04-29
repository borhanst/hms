from django.contrib.auth.decorators import login_required
from core.decorators import admin_required, module_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date

from .models import EmployeeProfile, Attendance, LeaveRequest
from .forms import EmployeeProfileForm, AttendanceForm, LeaveRequestForm, LeaveReviewForm
from core.models import User


@login_required
@module_required("hr")
def hr_dashboard(request):
    total_employees = EmployeeProfile.objects.count()
    today = date.today()
    today_present = Attendance.objects.filter(date=today, status="PRESENT").count()
    today_absent = Attendance.objects.filter(date=today, status="ABSENT").count()
    pending_leaves = LeaveRequest.objects.filter(status="PENDING").count()
    recent_leaves = LeaveRequest.objects.select_related("employee")[:10]
    context = {
        "total_employees": total_employees,
        "today_present": today_present,
        "today_absent": today_absent,
        "pending_leaves": pending_leaves,
        "recent_leaves": recent_leaves,
    }
    return render(request, "hr/hr_dashboard.html", context)


@login_required
@module_required("hr")
def employee_list(request):
    employees = EmployeeProfile.objects.select_related("user").all()
    paginator = Paginator(employees, 15)
    return render(request, "hr/employee_list.html", {"page_obj": paginator.get_page(request.GET.get("page")), "employees": paginator.get_page(request.GET.get("page"))})


@login_required
@module_required("hr")
@admin_required
def employee_create(request):
    if request.method == "POST":
        form = EmployeeProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee profile created.")
            return redirect("hr:employee_list")
    else:
        form = EmployeeProfileForm()
    return render(request, "hr/employee_form.html", {"form": form, "title": "Add Employee Profile"})


@login_required
@module_required("hr")
@admin_required
def employee_edit(request, pk):
    emp = get_object_or_404(EmployeeProfile, pk=pk)
    if request.method == "POST":
        form = EmployeeProfileForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee profile updated.")
            return redirect("hr:employee_list")
    else:
        form = EmployeeProfileForm(instance=emp)
    return render(request, "hr/employee_form.html", {"form": form, "title": "Edit Employee Profile"})


@login_required
@module_required("hr")
@admin_required
def employee_delete(request, pk):
    emp = get_object_or_404(EmployeeProfile, pk=pk)
    if request.method == "POST":
        emp.delete()
        messages.success(request, "Employee profile deleted.")
        return redirect("hr:employee_list")
    return render(request, "hr/employee_confirm_delete.html", {"object": emp})


@login_required
@module_required("hr")
def attendance_list(request):
    records = Attendance.objects.select_related("employee").all()
    att_date = request.GET.get("date", "")
    if att_date:
        records = records.filter(date=att_date)
    paginator = Paginator(records, 20)
    return render(request, "hr/attendance_list.html", {
        "page_obj": paginator.get_page(request.GET.get("page")),
        "records": paginator.get_page(request.GET.get("page")),
        "att_date": att_date,
    })


@login_required
@module_required("hr")
def attendance_create(request):
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attendance recorded.")
            return redirect("hr:attendance_list")
    else:
        form = AttendanceForm(initial={"date": date.today()})
    return render(request, "hr/attendance_form.html", {"form": form, "title": "Record Attendance"})


@login_required
@module_required("hr")
def leave_list(request):
    leaves = LeaveRequest.objects.select_related("employee").all()
    status = request.GET.get("status", "")
    if status:
        leaves = leaves.filter(status=status)
    paginator = Paginator(leaves, 15)
    return render(request, "hr/leave_list.html", {
        "page_obj": paginator.get_page(request.GET.get("page")),
        "leaves": paginator.get_page(request.GET.get("page")),
        "status_choices": LeaveRequest.STATUS_CHOICES,
    })


@login_required
@module_required("hr")
def leave_create(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.save()
            messages.success(request, "Leave request submitted.")
            return redirect("hr:leave_list")
    else:
        form = LeaveRequestForm()
    return render(request, "hr/leave_form.html", {"form": form, "title": "Request Leave"})


@login_required
@module_required("hr")
@admin_required
def leave_review(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == "POST":
        form = LeaveReviewForm(request.POST, instance=leave)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.reviewed_by = request.user
            leave.save()
            messages.success(request, "Leave request reviewed.")
            return redirect("hr:leave_list")
    else:
        form = LeaveReviewForm(instance=leave)
    return render(request, "hr/leave_review.html", {"form": form, "leave": leave})
