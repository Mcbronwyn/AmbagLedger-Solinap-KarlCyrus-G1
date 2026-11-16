from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('user_id', 'email', 'full_name', 'role', 'contact_number', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name', 'contact_number')
    ordering = ('-created_at',)

    fieldsets = (
        ('Credentials', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'contact_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('last_login', 'created_at')}),
    )
    readonly_fields = ('created_at', 'last_login')

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'full_name', 'role', 'contact_number', 'password1', 'password2', 'is_staff', 'is_active'),
            },
        ),
    )