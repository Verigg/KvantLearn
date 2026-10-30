from django import forms
from tinymce.widgets import TinyMCE
from .models import Lesson, Material, Module


class MaterialForm(forms.ModelForm):
    """Форма создания и редактирования учебного материала."""

    class Meta:
        model = Material
        fields = ['title', 'short_description', 'direction', 'cover_image', 'is_published']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
                    'placeholder': 'Например: Введение в разработку на Python',
                }
            ),
            'short_description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
                    'placeholder': 'Кратко опишите, чему научатся ученики...',
                }
            ),
            'direction': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 bg-white',
                }
            ),
            'cover_image': forms.FileInput(
                attrs={
                    'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100',
                }
            ),
            'is_published': forms.CheckboxInput(
                attrs={
                    'class': 'w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 focus:ring-2',
                }
            ),
        }
        labels = {
            'title': 'Название материала',
            'short_description': 'Краткое описание (до 300 символов)',
            'direction': 'Направление',
            'cover_image': 'Обложка курса (необязательно)',
            'is_published': 'Опубликовать материал (будет виден всем ученикам)',
        }


class ModuleForm(forms.ModelForm):
    """Форма добавления или переименования модуля."""

    class Meta:
        model = Module
        fields = ['title']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
                    'placeholder': 'Название модуля (например, «Основы синтаксиса»)',
                }
            ),
        }
        labels = {
            'title': 'Название модуля',
        }


class LessonForm(forms.ModelForm):
    """Форма редактирования урока с TinyMCE редактором."""

    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}),
        required=False,
        label='Содержимое урока',
    )

    class Meta:
        model = Lesson
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
                    'placeholder': 'Название урока (например, «Переменные и типы данных»)',
                }
            ),
        }
        labels = {
            'title': 'Заголовок урока',
            'content': 'Содержимое урока',
        }

