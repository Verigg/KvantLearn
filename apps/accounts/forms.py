from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class CustomUserRegistrationForm(UserCreationForm):
    """Форма регистрации нового педагога в системе."""

    full_name = forms.CharField(
        label='ФИО педагога',
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Иванов Иван Иванович',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
            }
        ),
    )

    consent = forms.BooleanField(
        required=True,
        label='Я согласен на обработку персональных данных',
        error_messages={
            'required': 'Необходимо согласие на обработку персональных данных',
        },
        widget=forms.CheckboxInput(
            attrs={
                'id': 'consent',
                'class': 'w-4 h-4 text-indigo-600 bg-gray-100 border-gray-300 rounded focus:ring-indigo-500 focus:ring-2 cursor-pointer',
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'full_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['username'].help_text = 'Только буквы, цифры и знаки @/./+/-/_'
        self.fields['username'].widget.attrs.update(
            {
                'placeholder': 'teacher_ivan',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
            }
        )
        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': '••••••••',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
            }
        )
        self.fields['password2'].label = 'Повторите пароль'
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': '••••••••',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
            }
        )

    def clean_consent(self):
        consent = self.cleaned_data.get('consent')
        if not consent:
            raise forms.ValidationError('Необходимо согласие на обработку персональных данных')
        return consent

    def save(self, commit=True):
        from django.utils import timezone

        user = super().save(commit=False)
        user.role = CustomUser.ROLE_TEACHER
        user.is_approved = False  # Требуется подтверждение администратора
        user.consent_personal_data = True
        user.consent_date = timezone.now()
        user.consent_version = '1.0'
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """Форма входа с кастомным оформлением Tailwind."""

    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите ваш логин',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
            }
        ),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '••••••••',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm text-gray-900 placeholder-gray-400',
            }
        ),
    )
