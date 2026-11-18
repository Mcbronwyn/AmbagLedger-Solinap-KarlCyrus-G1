from django.contrib import admin
from .models import Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_id', 'section_name', 'academic_term', 'invite_code', 'treasurer', 'created_at')
    search_fields = ('section_name', 'academic_term', 'invite_code', 'treasurer__email')
    readonly_fields = ('invite_code', 'created_at')