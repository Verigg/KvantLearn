"""URL Configuration for KvantLearn project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.catalog import views as catalog_views
from apps.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('privacy/', core_views.PrivacyView.as_view(), name='privacy'),
    path('terms/', core_views.TermsView.as_view(), name='terms'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('catalog/material/<slug:slug>/', catalog_views.MaterialDetailView.as_view(), name='catalog_material_compat'),
    path('catalog/lesson/<int:pk>/', catalog_views.LessonDetailView.as_view(), name='catalog_lesson_compat'),
    path('catalog/<slug:slug>/', catalog_views.MaterialDetailView.as_view(), name='catalog_detail_compat'),
    path('catalog/', catalog_views.MaterialListView.as_view(), name='catalog_list_compat'),
    path('materials/', include('apps.catalog.urls', namespace='catalog')),
    path('editor/', include('apps.catalog.urls_editor', namespace='editor')),
    path('tinymce/', include('tinymce.urls')),
    path('', include('apps.core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
