"""URL Configuration for KvantLearn project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('privacy/', core_views.PrivacyView.as_view(), name='privacy'),
    path('terms/', core_views.TermsView.as_view(), name='terms'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('materials/', include('apps.catalog.urls', namespace='catalog')),
    path('editor/', include('apps.catalog.urls_editor', namespace='editor')),
    path('tinymce/', include('tinymce.urls')),
    path('', include('apps.core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
