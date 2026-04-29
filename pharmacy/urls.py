from django.urls import path
from . import views

app_name = "pharmacy"

urlpatterns = [
    path("", views.pharmacy_dashboard, name="pharmacy_dashboard"),
    path("medicines/", views.medicine_list, name="medicine_list"),
    path("medicines/create/", views.medicine_create, name="medicine_create"),
    path("medicines/<int:pk>/edit/", views.medicine_edit, name="medicine_edit"),
    path("medicines/<int:pk>/delete/", views.medicine_delete, name="medicine_delete"),
    path("medicines/<int:pk>/dispose-expired/", views.medicine_dispose_expired, name="medicine_dispose_expired"),
    path("dispensing/", views.dispensing_list, name="dispensing_list"),
    path("dispensing/create/", views.dispensing_create, name="dispensing_create"),
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/create/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/edit/", views.supplier_edit, name="supplier_edit"),
    path("purchases/", views.purchase_list, name="purchase_list"),
    path("purchases/create/", views.purchase_create, name="purchase_create"),
    path("purchases/<int:pk>/", views.purchase_detail, name="purchase_detail"),
    path("purchases/<int:pk>/complete/", views.purchase_complete, name="purchase_complete"),
    path("sales/", views.sale_list, name="sale_list"),
    path("sales/create/", views.sale_create, name="sale_create"),
    path("sales/<int:pk>/", views.sale_detail, name="sale_detail"),
    path("stock-movements/", views.stock_movement_list, name="stock_movement_list"),
    path("reports/", views.pharmacy_reports, name="pharmacy_reports"),
]
