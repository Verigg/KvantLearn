from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Настройка отображения пользователей в Django Admin."""

    list_display = (
        'username',
        'full_name',
        'role',
        'is_approved',
        'is_staff',
        'is_superuser',
        'created_at',
    )
    list_filter = ('role', 'is_approved', 'is_staff', 'is_superuser')
    search_fields = ('username', 'full_name', 'email')
    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'Роль и статус в KvantLearn',
            {
                'fields': ('role', 'is_approved', 'full_name', 'consent_personal_data', 'consent_date', 'consent_version'),
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Роль и статус в KvantLearn',
            {
                'fields': ('role', 'is_approved', 'full_name', 'consent_personal_data', 'consent_date', 'consent_version'),
            },
        ),
    )
