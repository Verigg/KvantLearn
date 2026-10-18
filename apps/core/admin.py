from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'hero_title')

    def has_add_permission(self, request):
        # Только 1 объект настроек
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
