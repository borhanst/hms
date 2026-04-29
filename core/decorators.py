from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

from .permissions import can_access_module


def role_required(*roles):
    """Decorator that restricts view access to users with specific roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("core:login")
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access this page.")
            return redirect("core:dashboard")
        return wrapper
    return decorator


def module_required(module_key):
    """Restrict a view to users whose role can access a module."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("core:login")
            if can_access_module(request.user, module_key):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access this page.")
            return redirect("core:dashboard")
        return wrapper
    return decorator


def admin_required(view_func):
    return role_required("ADMIN")(view_func)


def doctor_required(view_func):
    return role_required("DOCTOR")(view_func)


def staff_required(view_func):
    """Admin or Receptionist"""
    return role_required("ADMIN", "RECEPTIONIST")(view_func)
