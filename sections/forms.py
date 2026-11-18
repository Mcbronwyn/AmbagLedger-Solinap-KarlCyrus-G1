from django import forms
from .models import MAX_ACTIVE_STUDENTS, Section, SectionMember


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['section_name', 'academic_term']
        labels = {
            'section_name': 'Class Section Name',
            'academic_term': 'Academic Term',
        }
        widgets = {
            'section_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CSIT327-G1',
                'maxlength': '100',
            }),
            'academic_term': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1st Semester 2026-2027',
                'maxlength': '50',
            }),
        }
        help_texts = {
            'section_name': 'Course code and section identifier (e.g., CSIT327-G1).',
            'academic_term': 'Semester and academic year for this class ledger.',
        }

    def clean_section_name(self):
        value = self.cleaned_data['section_name'].strip()
        if not value:
            raise forms.ValidationError('Section name cannot be blank.')
        return value

    def clean_academic_term(self):
        value = self.cleaned_data['academic_term'].strip()
        if not value:
            raise forms.ValidationError('Academic term cannot be blank.')
        return value


class JoinSectionForm(forms.Form):
    invite_code = forms.CharField(
        max_length=10,
        label='Section Invite Code',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., A8K29P4X',
            'style': 'text-transform: uppercase; letter-spacing: 0.08em;',
        }),
        help_text='Enter the 8-character alphanumeric invite code provided by your class treasurer.',
    )
    student_id_number = forms.CharField(
        max_length=20,
        label='University Student ID Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 24-1585-641',
        }),
        help_text='Your official institutional ID number for roster verification.',
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_invite_code(self):
        code = self.cleaned_data['invite_code'].strip().upper()
        if not code:
            raise forms.ValidationError('Invite code is required.')
        try:
            section = Section.objects.get(invite_code=code)
        except Section.DoesNotExist:
            raise forms.ValidationError('Invalid invite code. No matching class section was found.')
        self.cleaned_data['section'] = section
        return code

    def clean_student_id_number(self):
        student_id = self.cleaned_data['student_id_number'].strip()
        if not student_id:
            raise forms.ValidationError('Student ID number cannot be blank.')
        return student_id

    def clean(self):
        cleaned_data = super().clean()
        section = cleaned_data.get('section')
        if not section or not self.user:
            return cleaned_data

        # BR-04: Student can only be enrolled once per section
        if SectionMember.objects.filter(section=section, user=self.user).exists():
            raise forms.ValidationError(
                f'You are already enrolled in {section.section_name} ({section.academic_term}).'
            )

        # BR-05: Section roster cannot exceed 50 active students
        if section.active_member_count >= MAX_ACTIVE_STUDENTS:
            raise forms.ValidationError(
                f'{section.section_name} has reached its maximum capacity of {MAX_ACTIVE_STUDENTS} active students.'
            )

        return cleaned_data