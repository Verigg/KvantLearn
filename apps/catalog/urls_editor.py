from django.urls import path

from . import views

app_name = 'editor'

urlpatterns = [
    # Список материалов в редакторе
    path('', views.EditorMaterialListView.as_view(), name='material_list'),
    path('materials/new/', views.EditorMaterialCreateView.as_view(), name='material_create'),
    path('materials/<slug:slug>/edit/', views.EditorMaterialEditView.as_view(), name='material_edit'),
    path('materials/<slug:slug>/delete/', views.EditorMaterialDeleteView.as_view(), name='material_delete'),

    # Модули (inline управление)
    path('materials/<slug:slug>/modules/new/', views.EditorModuleCreateView.as_view(), name='module_create'),
    path('modules/<int:pk>/rename/', views.EditorModuleRenameView.as_view(), name='module_rename'),
    path('modules/<int:pk>/delete/', views.EditorModuleDeleteView.as_view(), name='module_delete'),
    path('modules/<int:pk>/move-up/', views.EditorModuleMoveUpView.as_view(), name='module_move_up'),
    path('modules/<int:pk>/move-down/', views.EditorModuleMoveDownView.as_view(), name='module_move_down'),

    # Уроки
    path('modules/<int:pk>/lessons/new/', views.EditorLessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/edit/', views.EditorLessonEditView.as_view(), name='lesson_edit'),
    path('lessons/<int:pk>/delete/', views.EditorLessonDeleteView.as_view(), name='lesson_delete'),
    path('lessons/<int:pk>/move-up/', views.EditorLessonMoveUpView.as_view(), name='lesson_move_up'),
    path('lessons/<int:pk>/move-down/', views.EditorLessonMoveDownView.as_view(), name='lesson_move_down'),

    # Загрузка изображений из TinyMCE
    path('upload-image/', views.editor_upload_image, name='upload_image'),
]
