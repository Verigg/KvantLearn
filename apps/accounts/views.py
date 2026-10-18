from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from .forms import CustomLoginForm, CustomUserRegistrationForm


class UserRegisterView(CreateView):
    """Регистрация нового педагога с ожиданием подтверждения."""

    template_name = 'accounts/register.html'
    form_class = CustomUserRegistrationForm
    success_url = reverse_lazy('accounts:pending')

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            'Регистрация успешна! Ваш аккаунт ожидает подтверждения администратором.'
        )
        # Вход не выполняется автоматически, пока админ не подтвердит
        return redirect(self.success_url)


class UserLoginView(LoginView):
    """Вход пользователей в систему."""

    template_name = 'accounts/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if not user.is_approved and not user.is_administrator:
            return reverse_lazy('accounts:pending')
        return reverse_lazy('editor:material_list')


class UserLogoutView(View):
    """Выход из системы (поддерживает GET и POST)."""

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Вы успешно вышли из системы.')
        return redirect('core:home')

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Вы успешно вышли из системы.')
        return redirect('core:home')


class PendingApprovalView(TemplateView):
    """Информационная страница об ожидании одобрения аккаунта."""

    template_name = 'accounts/pending.html'
