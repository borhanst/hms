import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def export_to_csv(model, fields, filename=None):
    """Return a view function that exports model data as CSV."""
    if filename is None:
        filename = model._meta.model_name

    @login_required
    def export_view(request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        writer = csv.writer(response)
        writer.writerow([f.replace("_", " ").title() for f in fields])
        for obj in model.objects.all()[:5000]:
            writer.writerow([getattr(obj, f, "") for f in fields])
        return response

    return export_view
