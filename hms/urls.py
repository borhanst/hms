from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("doctors/", include("doctors.urls")),
    path("patients/", include("patients.urls")),
    path("reports/", include("reports.urls")),
    path("prescriptions/", include("prescriptions.urls")),
    path("appointments/", include("appointments.urls")),
    path("billing/", include("billing.urls")),
    path("pharmacy/", include("pharmacy.urls")),
    path("beds/", include("beds.urls")),
    path("nursing/", include("nursing.urls")),
    path("hr/", include("hr.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
