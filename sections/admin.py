from django.contrib import admin
from .models import Section, SectionMember


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_id', 'section_name', 'academic_term', 'invite_code', 'treasurer', 'created_at')
    search_fields = ('section_name', 'academic_term', 'invite_code', 'treasurer__email')
    readonly_fields = ('invite_code', 'created_at')


@admin.register(SectionMember)
class SectionMemberAdmin(admin.ModelAdmin):
    list_display = ('membership_id', 'section', 'user', 'student_id_number', 'is_active', 'joined_at')
    list_filter = ('is_active', 'section')
    search_fields = ('student_id_number', 'user__full_name', 'user__email', 'section__section_name')