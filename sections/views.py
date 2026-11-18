from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import RestrictedError
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import treasurer_required
from .forms import SectionForm
from .models import Section


def _get_owned_section_or_403(request, section_id):
    """Fetch section by PK and enforce that request.user is its owning Treasurer."""
    section = get_object_or_404(Section, section_id=section_id)
    if section.treasurer_id != request.user.user_id:
        return None, render(request, '403.html', status=403)
    return section, None


@login_required
@treasurer_required
def section_list(request):
    sections = Section.objects.filter(treasurer=request.user)
    return render(request, 'sections/section_list.html', {
        'sections': sections,
    })


@login_required
@treasurer_required
def section_create(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.treasurer = request.user
            section.save()
            messages.success(
                request,
                f'Section "{section.section_name}" created! Invite Code: {section.invite_code}',
            )
            return redirect('sections:section_detail', section_id=section.section_id)
    else:
        form = SectionForm()

    return render(request, 'sections/section_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
@treasurer_required
def section_detail(request, section_id):
    section, forbidden_response = _get_owned_section_or_403(request, section_id)
    if forbidden_response:
        return forbidden_response

    return render(request, 'sections/section_detail.html', {
        'section': section,
    })


@login_required
@treasurer_required
def section_update(request, section_id):
    section, forbidden_response = _get_owned_section_or_403(request, section_id)
    if forbidden_response:
        return forbidden_response

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, f'Section "{section.section_name}" updated.')
            return redirect('sections:section_detail', section_id=section.section_id)
    else:
        form = SectionForm(instance=section)

    return render(request, 'sections/section_form.html', {
        'form': form,
        'section': section,
        'is_edit': True,
    })


@login_required
@treasurer_required
def section_delete(request, section_id):
    section, forbidden_response = _get_owned_section_or_403(request, section_id)
    if forbidden_response:
        return forbidden_response

    if request.method == 'POST':
        section_name = section.section_name
        try:
            section.delete()
            messages.success(request, f'Section "{section_name}" has been deleted.')
            return redirect('sections:section_list')
        except RestrictedError:
            messages.error(
                request,
                f'Cannot delete "{section_name}" because it has linked collection drives.',
            )
            return redirect('sections:section_detail', section_id=section.section_id)

    return render(request, 'sections/section_confirm_delete.html', {
        'section': section,
    })