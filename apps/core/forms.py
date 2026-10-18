from django import forms
from apps.accounts.models import CustomUser
from .models import SiteSettings


class SiteSettingsForm(forms.ModelForm):
    """Форма редактирования настроек сайта администратором."""

    class Meta:
        model = SiteSettings
        fields = [
            'site_name',
            'site_description',
            'hero_title',
            'hero_subtitle',
            'contact_email',
            'footer_text',
        ]
        widgets = {
            'site_name': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900',
                }
            ),
            'site_description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900',
                }
            ),
            'hero_title': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900',
                }
            ),
            'hero_subtitle': forms.Textarea(
                attrs={
                    'rows': 3,
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900',
                }
            ),
            'contact_email': forms.EmailInput(
                attrs={
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900',
                }
            ),
            'footer_text': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900',
                }
            ),
        }
        labels = {
            'site_name': 'Название платформы',
            'site_description': 'SEO-описание платформы',
            'hero_title': 'Главный заголовок на баннере (Hero)',
            'hero_subtitle': 'Подзаголовок баннера',
            'contact_email': 'Контактный email',
            'footer_text': 'Текст в подвале сайта',
        }


class UserStatusUpdateForm(forms.ModelForm):
    """Форма быстрого изменения статуса и роли пользователя."""

    class Meta:
        model = CustomUser
        fields = ['role', 'is_approved']
        widgets = {
            'role': forms.Select(
                attrs={
                    'class': 'text-xs px-2.5 py-1.5 rounded-lg border border-gray-300 focus:ring-1 focus:ring-indigo-500 bg-white',
                }
            ),
            'is_approved': forms.CheckboxInput(
                attrs={
                    'class': 'w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 focus:ring-2',
                }
            ),
        }
