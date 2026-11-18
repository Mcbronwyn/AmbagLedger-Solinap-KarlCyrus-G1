from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import RestrictedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import member_required, treasurer_required
from .forms import JoinSectionForm, SectionForm
from .models import MAX_ACTIVE_STUDENTS, Section, SectionMember


def _get_owned_section_or_403(request, section_id):
    """Fetch section by PK and enforce that request.user is its owning Treasurer."""
    section = get_object_or_404(Section, section_id=section_id)
    if section.treasurer_id != request.user.user_id:
        return None, render(request, '403.html', status=403)
    return section, None


# ---------------------------------------------------------------------------
# TREASURER VIEWS (F-02 Section CRUD & F-03 Roster Moderation)
# ---------------------------------------------------------------------------

@login_required
@treasurer_required
def section_list(request):
    sections = Section.objects.filter(treasurer=request.user)
    return render(request, 'sections/section_list.html', {
        'sections': sections,
        'max_students': MAX_ACTIVE_STUDENTS,
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

    memberships = section.memberships.select_related('user').all()
    active_count = section.active_member_count

    return render(request, 'sections/section_detail.html', {
        'section': section,
        'memberships': memberships,
        'active_count': active_count,
        'max_students': MAX_ACTIVE_STUDENTS,
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


@login_required
@treasurer_required
@require_POST
def toggle_member_status(request, section_id, membership_id):
    section, forbidden_response = _get_owned_section_or_403(request, section_id)
    if forbidden_response:
        return forbidden_response

    membership = get_object_or_404(SectionMember, membership_id=membership_id, section=section)

    # BR-05: Enforce 50 active student cap before reactivating a removed student
    if not membership.is_active and section.active_member_count >= MAX_ACTIVE_STUDENTS:
        messages.error(
            request,
            f'Cannot reactivate {membership.user.full_name}: roster is at the {MAX_ACTIVE_STUDENTS}-student limit.',
        )
        return redirect('sections:section_detail', section_id=section.section_id)

    membership.is_active = not membership.is_active
    membership.save(update_fields=['is_active'])

    status_label = 'Active' if membership.is_active else 'Removed'
    messages.success(
        request,
        f'Updated {membership.user.full_name} ({membership.student_id_number}) status to {status_label}.',
    )
    return redirect('sections:section_detail', section_id=section.section_id)


@login_required
@treasurer_required
@require_POST
def remove_member(request, section_id, membership_id):
    section, forbidden_response = _get_owned_section_or_403(request, section_id)
    if forbidden_response:
        return forbidden_response

    membership = get_object_or_404(SectionMember, membership_id=membership_id, section=section)
    student_name = membership.user.full_name
    try:
        membership.delete()
        messages.success(request, f'Removed {student_name} from {section.section_name}.')
    except RestrictedError:
        messages.error(
            request,
            f'Cannot permanently delete {student_name} because they have linked payment records. Deactivate them instead.',
        )
    return redirect('sections:section_detail', section_id=section.section_id)


# ---------------------------------------------------------------------------
# MEMBER VIEWS (F-03 Join via Invite Code & View Joined Sections)
# ---------------------------------------------------------------------------

@login_required
@member_required
def member_section_list(request):
    memberships = SectionMember.objects.filter(user=request.user).select_related(
        'section', 'section__treasurer'
    )
    return render(request, 'sections/member_section_list.html', {
        'memberships': memberships,
    })


@login_required
@member_required
def join_section(request):
    if request.method == 'POST':
        form = JoinSectionForm(request.POST, user=request.user)
        if form.is_valid():
            section = form.cleaned_data['section']
            try:
                SectionMember.objects.create(
                    section=section,
                    user=request.user,
                    student_id_number=form.cleaned_data['student_id_number'],
                )
            except IntegrityError:
                messages.error(request, 'You are already enrolled in this class section.')
                return redirect('sections:member_section_list')

            messages.success(
                request,
                f'Successfully joined {section.section_name} ({section.academic_term})!',
            )
            return redirect('sections:member_section_detail', section_id=section.section_id)
    else:
        form = JoinSectionForm(user=request.user)

    return render(request, 'sections/join_section.html', {
        'form': form,
    })


@login_required
@member_required
def member_section_detail(request, section_id):
    section = get_object_or_404(Section, section_id=section_id)
    membership = SectionMember.objects.filter(section=section, user=request.user).first()
    if not membership:
        return render(request, '403.html', status=403)

    return render(request, 'sections/member_section_detail.html', {
        'section': section,
        'membership': membership,
        'active_count': section.active_member_count,
        'max_students': MAX_ACTIVE_STUDENTS,
    })