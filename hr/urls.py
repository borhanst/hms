from django.urls import path
from . import views

app_name = "hr"

urlpatterns = [
    path("", views.hr_dashboard, name="hr_dashboard"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/create/", views.attendance_create, name="attendance_create"),
    path("leaves/", views.leave_list, name="leave_list"),
    path("leaves/create/", views.leave_create, name="leave_create"),
    path("leaves/<int:pk>/review/", views.leave_review, name="leave_review"),
]
