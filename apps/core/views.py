from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView, UpdateView

from apps.accounts.models import CustomUser
from apps.catalog.models import Material
from .forms import SiteSettingsForm
from .models import PageVisit, SiteSettings


class AdminRequiredMixin(UserPassesTestMixin):
    """Ограничение доступа: только для подтвержденных администраторов платформы."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.is_administrator and user.is_approved

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        raise PermissionDenied("Доступ разрешен только подтвержденным администраторам.")



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


class PrivacyView(TemplateView):
    """Страница политики конфиденциальности (152-ФЗ)."""

    template_name = 'core/privacy.html'


class TermsView(TemplateView):
    """Страница пользовательского соглашения."""

    template_name = 'core/terms.html'


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


# =====================================================================
# Раздел аналитики и статистики посещений (для Администраторов)
# =====================================================================

def process_stats_queryset(base_qs, period_param: str):
    """
    Универсальный обработчик фильтрации и группировки посещений по периодам.
    - '3m' (по умолчанию): за последние 90 дней с группировкой по дням (TruncDate);
    - 'year': за текущий календарный год с группировкой по дням (TruncDate);
    - 'all': за все время с группировкой по месяцам (TruncMonth) для читаемости графика.
    """
    now = timezone.now()
    if period_param not in ('3m', 'year', 'all'):
        period_param = '3m'

    if period_param == '3m':
        since = now - timedelta(days=90)
        qs = base_qs.filter(timestamp__gte=since)
        daily = (
            qs.annotate(d=TruncDate('timestamp'))
            .values('d')
            .annotate(count=Count('id'))
            .order_by('d')
        )
        counts_by_date = {item['d']: item['count'] for item in daily if item['d']}
        chart_labels = []
        chart_data = []
        current_d = since.date()
        end_d = now.date()
        while current_d <= end_d:
            chart_labels.append(current_d.strftime('%d.%m'))
            chart_data.append(counts_by_date.get(current_d, 0))
            current_d += timedelta(days=1)

    elif period_param == 'year':
        qs = base_qs.filter(timestamp__year=now.year)
        daily = (
            qs.annotate(d=TruncDate('timestamp'))
            .values('d')
            .annotate(count=Count('id'))
            .order_by('d')
        )
        counts_by_date = {item['d']: item['count'] for item in daily if item['d']}
        chart_labels = []
        chart_data = []
        current_d = date(now.year, 1, 1)
        end_d = now.date()
        while current_d <= end_d:
            chart_labels.append(current_d.strftime('%d.%m'))
            chart_data.append(counts_by_date.get(current_d, 0))
            current_d += timedelta(days=1)

    else:  # 'all'
        qs = base_qs
        monthly = (
            qs.annotate(m=TruncMonth('timestamp'))
            .values('m')
            .annotate(count=Count('id'))
            .order_by('m')
        )
        chart_labels = []
        chart_data = []
        for item in monthly:
            if item['m']:
                chart_labels.append(item['m'].strftime('%m.%Y'))
                chart_data.append(item['count'])

    total_visits = qs.count()
    unique_sessions = (
        qs.exclude(session_key='')
        .values('session_key')
        .distinct()
        .count()
    )

    return {
        'queryset': qs,
        'period': period_param,
        'total_visits': total_visits,
        'unique_sessions': unique_sessions,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }


class StatsOverviewView(AdminRequiredMixin, TemplateView):
    """Главная страница аналитики посещаемости сайта для администраторов."""

    template_name = 'core/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = self.request.GET.get('period', '3m').strip().lower()
        stats = process_stats_queryset(PageVisit.objects.all(), period)
        qs = stats['queryset']

        # Топ-5 материалов по просмотрам
        top_mat_data = (
            qs.filter(material__isnull=False)
            .values('material_id')
            .annotate(views_count=Count('id'))
            .order_by('-views_count')[:5]
        )
        mat_ids = [item['material_id'] for item in top_mat_data]
        materials_by_id = {
            m.id: m for m in Material.objects.filter(id__in=mat_ids).select_related('author')
        }
        top_materials = []
        for item in top_mat_data:
            mat = materials_by_id.get(item['material_id'])
            if mat:
                top_materials.append({
                    'material': mat,
                    'views_count': item['views_count'],
                })

        # Топ-5 педагогов по просмотрам их материалов
        top_teach_data = (
            qs.filter(teacher__isnull=False)
            .values('teacher_id')
            .annotate(views_count=Count('id'))
            .order_by('-views_count')[:5]
        )
        teacher_ids = [item['teacher_id'] for item in top_teach_data]
        teachers_by_id = {u.id: u for u in CustomUser.objects.filter(id__in=teacher_ids)}
        top_teachers = []
        for item in top_teach_data:
            teach = teachers_by_id.get(item['teacher_id'])
            if teach:
                top_teachers.append({
                    'teacher': teach,
                    'views_count': item['views_count'],
                })

        context.update({
            'period': stats['period'],
            'total_visits': stats['total_visits'],
            'unique_sessions': stats['unique_sessions'],
            'top_materials': top_materials,
            'top_teachers': top_teachers,
            'chart_labels': stats['chart_labels'],
            'chart_data': stats['chart_data'],
        })
        return context


class MaterialStatsView(AdminRequiredMixin, TemplateView):
    """Детальная страница статистики посещений конкретного учебного материала."""

    template_name = 'core/stats_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = get_object_or_404(
            Material.objects.select_related('author'),
            pk=self.kwargs.get('pk')
        )
        period = self.request.GET.get('period', '3m').strip().lower()
        base_qs = PageVisit.objects.filter(material=material)
        stats = process_stats_queryset(base_qs, period)

        # Популярные страницы уроков внутри материала
        lesson_visits = (
            stats['queryset']
            .filter(path__contains='/lesson')
            .values('path')
            .annotate(views_count=Count('id'))
            .order_by('-views_count')[:10]
        )

        context.update({
            'detail_type': 'material',
            'material': material,
            'period': stats['period'],
            'total_visits': stats['total_visits'],
            'unique_sessions': stats['unique_sessions'],
            'chart_labels': stats['chart_labels'],
            'chart_data': stats['chart_data'],
            'lesson_visits': lesson_visits,
        })
        return context


class TeacherStatsView(AdminRequiredMixin, TemplateView):
    """Детальная страница статистики посещений всех материалов конкретного педагога."""

    template_name = 'core/stats_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = get_object_or_404(CustomUser, pk=self.kwargs.get('pk'))
        period = self.request.GET.get('period', '3m').strip().lower()
        base_qs = PageVisit.objects.filter(teacher=teacher)
        stats = process_stats_queryset(base_qs, period)

        # Рейтинг материалов данного педагога по просмотрам за период
        mat_visits_data = (
            stats['queryset']
            .filter(material__isnull=False)
            .values('material_id')
            .annotate(views_count=Count('id'))
            .order_by('-views_count')[:10]
        )
        mat_ids = [item['material_id'] for item in mat_visits_data]
        mats_by_id = {m.id: m for m in Material.objects.filter(id__in=mat_ids)}
        teacher_materials = []
        for item in mat_visits_data:
            m = mats_by_id.get(item['material_id'])
            if m:
                teacher_materials.append({
                    'material': m,
                    'views_count': item['views_count'],
                })

        total_courses = Material.objects.filter(author=teacher).count()

        context.update({
            'detail_type': 'teacher',
            'teacher': teacher,
            'period': stats['period'],
            'total_visits': stats['total_visits'],
            'unique_sessions': stats['unique_sessions'],
            'chart_labels': stats['chart_labels'],
            'chart_data': stats['chart_data'],
            'teacher_materials': teacher_materials,
            'total_courses': total_courses,
        })
        return context

