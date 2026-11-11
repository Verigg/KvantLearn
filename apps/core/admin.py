from django.contrib import admin
from .models import PageVisit, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'hero_title')

    def has_add_permission(self, request):
        # Только 1 объект настроек
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('path', 'material', 'teacher', 'session_key', 'timestamp')
    list_filter = ('timestamp', 'material', 'teacher')
    search_fields = ('path', 'session_key', 'material__title', 'teacher__username', 'teacher__full_name')
    readonly_fields = ('path', 'material', 'teacher', 'session_key', 'timestamp')

