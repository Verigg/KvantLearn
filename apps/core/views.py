from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView

from apps.accounts.models import CustomUser
from apps.catalog.models import Material
from .forms import SiteSettingsForm
from .models import SiteSettings


class AdminRequiredMixin(UserPassesTestMixin):
    """Ограничение доступа: только для администраторов платформы."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.is_administrator)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        raise PermissionDenied("Доступ к разделу настроек разрешен только администраторам.")


class HomeView(TemplateView):
    """Главная страница: hero-блок, список последних материалов, рубрики."""

    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_materials'] = (
            Material.objects.filter(is_published=True)
            .select_related('author')
            .order_by('-created_at')[:8]
        )
        return context


class SiteSettingsEditView(AdminRequiredMixin, UpdateView):
    """Страница редактирования глобальных настроек сайта (/settings/)."""

    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = 'core/settings.html'
    success_url = reverse_lazy('core:settings')

    def get_object(self, queryset=None):
        return SiteSettings.get_settings()

    def form_valid(self, form):
        messages.success(self.request, 'Настройки сайта успешно обновлены!')
        return super().form_valid(form)


class UsersListView(AdminRequiredMixin, ListView):
    """Управление пользователями платформы (/settings/users/)."""

    model = CustomUser
    template_name = 'core/users_list.html'
    context_object_name = 'users_list'
    paginate_by = 30

    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by('-created_at')
        role = self.request.GET.get('role', '').strip()
        status = self.request.GET.get('status', '').strip()

        if role:
            queryset = queryset.filter(role=role)
        if status == 'pending':
            queryset = queryset.filter(is_approved=False)
        elif status == 'approved':
            queryset = queryset.filter(is_approved=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_role'] = self.request.GET.get('role', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['pending_count'] = CustomUser.objects.filter(is_approved=False).count()
        return context


class UserActionView(AdminRequiredMixin, View):
    """Быстрые действия над пользователем: подтвердить, отклонить, изменить роль."""

    def post(self, request, pk, *args, **kwargs):
        target_user = get_object_or_404(CustomUser, pk=pk)
        action = request.POST.get('action')

        # Защита от случайного снятия прав с самого себя
        if target_user == request.user and action in ('reject', 'make_teacher'):
            messages.warning(request, 'Вы не можете ограничить или изменить собственную учетную запись администратора.')
            return redirect('core:users_list')

        if action == 'approve':
            target_user.is_approved = True
            target_user.save(update_fields=['is_approved'])
            messages.success(request, f'Пользователь {target_user.display_name} подтвержден.')
        elif action == 'reject':
            target_user.is_approved = False
            target_user.save(update_fields=['is_approved'])
            messages.info(request, f'Подтверждение пользователя {target_user.display_name} отозвано.')
        elif action == 'make_admin':
            target_user.role = CustomUser.ROLE_ADMIN
            target_user.is_approved = True
            target_user.save(update_fields=['role', 'is_approved'])
            messages.success(request, f'Пользователю {target_user.display_name} назначена роль Администратора.')
        elif action == 'make_teacher':
            target_user.role = CustomUser.ROLE_TEACHER
            target_user.save(update_fields=['role'])
            messages.success(request, f'Пользователю {target_user.display_name} назначена роль Педагога.')

        return redirect('core:users_list')
