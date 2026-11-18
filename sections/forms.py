from django import forms
from .models import Section


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