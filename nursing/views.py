from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from core.decorators import module_required

from .models import NursingNote, MedicationAdministration
from .forms import NursingNoteForm, MedicationAdministrationForm


@login_required
@module_required("nursing")
def nursing_dashboard(request):
    total_notes = NursingNote.objects.count()
    urgent_notes = NursingNote.objects.filter(priority__in=["HIGH", "URGENT"]).count()
    today_admins = MedicationAdministration.objects.filter(administered_at__date__isnull=False).count()
    recent_notes = NursingNote.objects.select_related("patient", "nurse")[:10]
    recent_admins = MedicationAdministration.objects.select_related("patient", "nurse")[:10]
    context = {
        "total_notes": total_notes,
        "urgent_notes": urgent_notes,
        "today_admins": today_admins,
        "recent_notes": recent_notes,
        "recent_admins": recent_admins,
    }
    return render(request, "nursing/nursing_dashboard.html", context)


@login_required
@module_required("nursing")
def note_list(request):
    notes = NursingNote.objects.select_related("patient", "nurse").all()
    paginator = Paginator(notes, 15)
    return render(request, "nursing/note_list.html", {"page_obj": paginator.get_page(request.GET.get("page")), "notes": paginator.get_page(request.GET.get("page"))})


@login_required
@module_required("nursing")
def note_create(request):
    if request.method == "POST":
        form = NursingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            if request.user.role == "NURSE":
                note.nurse = request.user
            note.save()
            messages.success(request, "Nursing note added.")
            return redirect("nursing:note_list")
    else:
        form = NursingNoteForm()
    return render(request, "nursing/note_form.html", {"form": form, "title": "New Nursing Note"})


@login_required
@module_required("nursing")
def note_edit(request, pk):
    note = get_object_or_404(NursingNote, pk=pk)
    if request.method == "POST":
        form = NursingNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated.")
            return redirect("nursing:note_list")
    else:
        form = NursingNoteForm(instance=note)
    return render(request, "nursing/note_form.html", {"form": form, "title": "Edit Note"})


@login_required
@module_required("nursing")
def note_delete(request, pk):
    note = get_object_or_404(NursingNote, pk=pk)
    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted.")
        return redirect("nursing:note_list")
    return render(request, "nursing/note_confirm_delete.html", {"object": note})


@login_required
@module_required("nursing")
def medication_list(request):
    records = MedicationAdministration.objects.select_related("patient", "nurse").all()
    paginator = Paginator(records, 15)
    return render(request, "nursing/medication_list.html", {"page_obj": paginator.get_page(request.GET.get("page")), "records": paginator.get_page(request.GET.get("page"))})


@login_required
@module_required("nursing")
def medication_create(request):
    if request.method == "POST":
        form = MedicationAdministrationForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            if request.user.role == "NURSE":
                record.nurse = request.user
            record.save()
            messages.success(request, "Medication administered.")
            return redirect("nursing:medication_list")
    else:
        form = MedicationAdministrationForm()
    return render(request, "nursing/medication_form.html", {"form": form, "title": "Record Medication"})
