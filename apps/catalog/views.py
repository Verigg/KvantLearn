import os
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Max, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import LessonForm, MaterialForm, ModuleForm
from .models import Lesson, Material, Module


class ApprovedTeacherOrAdminMixin(AccessMixin):
    """Проверка: пользователь авторизован и подтвержден (или является админом)."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Неподтвержденных перенаправляем на страницу ожидания
        if not request.user.is_approved and not request.user.is_administrator:
            return redirect('accounts:pending')

        return super().dispatch(request, *args, **kwargs)


class MaterialAuthorOrAdminMixin(ApprovedTeacherOrAdminMixin):
    """Проверка прав: только автор материала или администратор."""

    def check_material_permission(self, material):
        if not (self.request.user.is_administrator or material.author == self.request.user):
            raise PermissionDenied("У вас нет прав для изменения этого материала.")


# =====================================================================
# Публичные представления
# =====================================================================

class MaterialListView(ListView):
    """Публичный каталог опубликованных учебных материалов."""

    model = Material
    template_name = 'catalog/material_list.html'
    context_object_name = 'materials'
    paginate_by = 12

    def get_queryset(self):
        queryset = Material.objects.filter(is_published=True).select_related('author')
        direction = self.request.GET.get('direction', '').strip()
        search_query = self.request.GET.get('q', '').strip()

        if direction:
            queryset = queryset.filter(direction=direction)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_direction'] = self.request.GET.get('direction', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class MaterialDetailView(DetailView):
    """Детальная страница учебного материала с оглавлением."""

    model = Material
    template_name = 'catalog/material_detail.html'
    context_object_name = 'material'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        material = super().get_object(queryset)
        user = self.request.user

        # Проверка видимости: неопубликованный материал доступен только автору или админу
        if not material.is_published:
            if not user.is_authenticated or (material.author != user and not user.is_administrator):
                raise Http404("Материал не найден или снят с публикации.")

        return material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.object
        modules = material.modules.prefetch_related('lessons').order_by('order', 'id')
        context['modules'] = modules
        # Первый урок для кнопки «Начать обучение»
        first_lesson = None
        for m in modules:
            first = m.lessons.order_by('order', 'id').first()
            if first:
                first_lesson = first
                break
        context['first_lesson'] = first_lesson
        return context


class LessonDetailView(DetailView):
    """Страница просмотра урока учеником."""

    model = Lesson
    template_name = 'catalog/lesson_detail.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        material_slug = self.kwargs.get('slug')
        lesson = get_object_or_404(
            Lesson.objects.select_related('module__material', 'module__material__author'),
            pk=self.kwargs.get('pk'),
            module__material__slug=material_slug,
        )
        material = lesson.module.material
        user = self.request.user

        # Проверка доступа к неопубликованному курсу
        if not material.is_published:
            if not user.is_authenticated or (material.author != user and not user.is_administrator):
                raise Http404("Материал не найден или снят с публикации.")

        return lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        material = lesson.module.material

        # Список всех уроков материала по порядку для навигации
        all_lessons = list(
            Lesson.objects.filter(module__material=material)
            .select_related('module')
            .order_by('module__order', 'module__id', 'order', 'id')
        )

        prev_lesson = None
        next_lesson = None
        for idx, item in enumerate(all_lessons):
            if item.pk == lesson.pk:
                if idx > 0:
                    prev_lesson = all_lessons[idx - 1]
                if idx < len(all_lessons) - 1:
                    next_lesson = all_lessons[idx + 1]
                break

        context['material'] = material
        context['modules'] = material.modules.prefetch_related('lessons').order_by('order', 'id')
        context['prev_lesson'] = prev_lesson
        context['next_lesson'] = next_lesson
        return context


# =====================================================================
# Редактор материалов (Педагог / Администратор)
# =====================================================================

class EditorMaterialListView(ApprovedTeacherOrAdminMixin, ListView):
    """Список материалов в редакторе: свои для педагога, все для админа."""

    model = Material
    template_name = 'catalog/editor_materials.html'
    context_object_name = 'materials'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user.is_administrator:
            return Material.objects.all().select_related('author').order_by('-created_at')
        return Material.objects.filter(author=user).select_related('author').order_by('-created_at')


class EditorMaterialCreateView(ApprovedTeacherOrAdminMixin, CreateView):
    """Создание нового материала."""

    model = Material
    form_class = MaterialForm
    template_name = 'catalog/editor_material_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        material = form.save()
        messages.success(self.request, f'Материал «{material.title}» успешно создан.')
        return redirect('editor:material_edit', slug=material.slug)


class EditorMaterialEditView(MaterialAuthorOrAdminMixin, UpdateView):
    """Редактирование материала и inline-управление модулями/уроками."""

    model = Material
    form_class = MaterialForm
    template_name = 'catalog/editor_material_edit.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        material = super().get_object(queryset)
        self.check_material_permission(material)
        return material

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        material = self.object
        context['modules'] = material.modules.prefetch_related('lessons').order_by('order', 'id')
        context['module_form'] = ModuleForm()
        return context

    def form_valid(self, form):
        material = form.save()
        messages.success(self.request, 'Изменения материала успешно сохранены.')
        return redirect('editor:material_edit', slug=material.slug)


class EditorMaterialDeleteView(MaterialAuthorOrAdminMixin, View):
    """Удаление материала."""

    def post(self, request, slug, *args, **kwargs):
        material = get_object_or_404(Material, slug=slug)
        self.check_material_permission(material)
        title = material.title
        material.delete()
        messages.success(request, f'Материал «{title}» удален.')
        return redirect('editor:material_list')


# =====================================================================
# Управление модулями (inline в редакторе)
# =====================================================================

class EditorModuleCreateView(MaterialAuthorOrAdminMixin, View):
    """Добавление нового модуля к материалу."""

    def post(self, request, slug, *args, **kwargs):
        material = get_object_or_404(Material, slug=slug)
        self.check_material_permission(material)

        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.material = material
            max_order = material.modules.aggregate(m=Max('order'))['m'] or 0
            module.order = max_order + 1
            module.save()
            messages.success(request, f'Модуль «{module.title}» добавлен.')
        else:
            messages.error(request, 'Ошибка при добавлении модуля. Укажите название.')

        return redirect('editor:material_edit', slug=material.slug)


class EditorModuleRenameView(MaterialAuthorOrAdminMixin, View):
    """Переименование модуля."""

    def post(self, request, pk, *args, **kwargs):
        module = get_object_or_404(Module.objects.select_related('material'), pk=pk)
        self.check_material_permission(module.material)

        title = request.POST.get('title', '').strip()
        if title:
            module.title = title
            module.save(update_fields=['title'])
            messages.success(request, 'Модуль переименован.')
        else:
            messages.error(request, 'Название модуля не может быть пустым.')

        return redirect('editor:material_edit', slug=module.material.slug)


class EditorModuleDeleteView(MaterialAuthorOrAdminMixin, View):
    """Удаление модуля со всеми уроками."""

    def post(self, request, pk, *args, **kwargs):
        module = get_object_or_404(Module.objects.select_related('material'), pk=pk)
        self.check_material_permission(module.material)

        material_slug = module.material.slug
        module_title = module.title
        module.delete()
        messages.success(request, f'Модуль «{module_title}» удален.')
        return redirect('editor:material_edit', slug=material_slug)


class EditorModuleMoveUpView(MaterialAuthorOrAdminMixin, View):
    """Перемещение модуля выше по списку."""

    def post(self, request, pk, *args, **kwargs):
        module = get_object_or_404(Module.objects.select_related('material'), pk=pk)
        self.check_material_permission(module.material)

        prev_module = (
            Module.objects.filter(material=module.material, order__lt=module.order)
            .order_by('-order')
            .first()
        )
        if prev_module:
            with transaction.atomic():
                module.order, prev_module.order = prev_module.order, module.order
                module.save(update_fields=['order'])
                prev_module.save(update_fields=['order'])

        return redirect('editor:material_edit', slug=module.material.slug)


class EditorModuleMoveDownView(MaterialAuthorOrAdminMixin, View):
    """Перемещение модуля ниже по списку."""

    def post(self, request, pk, *args, **kwargs):
        module = get_object_or_404(Module.objects.select_related('material'), pk=pk)
        self.check_material_permission(module.material)

        next_module = (
            Module.objects.filter(material=module.material, order__gt=module.order)
            .order_by('order')
            .first()
        )
        if next_module:
            with transaction.atomic():
                module.order, next_module.order = next_module.order, module.order
                module.save(update_fields=['order'])
                next_module.save(update_fields=['order'])

        return redirect('editor:material_edit', slug=module.material.slug)


# =====================================================================
# Управление уроками (inline и отдельная страница)
# =====================================================================

class EditorLessonCreateView(MaterialAuthorOrAdminMixin, View):
    """Быстрое создание урока в модуле с переходом к редактированию."""

    def post(self, request, pk, *args, **kwargs):
        module = get_object_or_404(Module.objects.select_related('material'), pk=pk)
        self.check_material_permission(module.material)

        title = request.POST.get('title', '').strip() or 'Новый урок'
        max_order = module.lessons.aggregate(m=Max('order'))['m'] or 0
        lesson = Lesson.objects.create(
            module=module,
            title=title,
            order=max_order + 1,
            content='<h2>Новый урок</h2><p>Здесь начинается текст урока.</p>',
        )
        messages.success(request, f'Урок «{lesson.title}» создан. Теперь вы можете заполнить его содержимое.')
        return redirect('editor:lesson_edit', pk=lesson.pk)


class EditorLessonEditView(MaterialAuthorOrAdminMixin, UpdateView):
    """Отдельная страница редактирования содержимого урока."""

    model = Lesson
    form_class = LessonForm
    template_name = 'catalog/editor_lesson_form.html'
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        lesson = super().get_object(queryset)
        self.check_material_permission(lesson.module.material)
        return lesson

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['material'] = self.object.module.material
        context['module'] = self.object.module
        return context

    def form_valid(self, form):
        lesson = form.save()
        messages.success(self.request, f'Урок «{lesson.title}» сохранен.')
        return redirect('editor:material_edit', slug=lesson.module.material.slug)


class EditorLessonDeleteView(MaterialAuthorOrAdminMixin, View):
    """Удаление урока."""

    def post(self, request, pk, *args, **kwargs):
        lesson = get_object_or_404(
            Lesson.objects.select_related('module__material'),
            pk=pk,
        )
        self.check_material_permission(lesson.module.material)

        material_slug = lesson.module.material.slug
        title = lesson.title
        lesson.delete()
        messages.success(request, f'Урок «{title}» удален.')
        return redirect('editor:material_edit', slug=material_slug)


class EditorLessonMoveUpView(MaterialAuthorOrAdminMixin, View):
    """Перемещение урока выше внутри своего модуля."""

    def post(self, request, pk, *args, **kwargs):
        lesson = get_object_or_404(Lesson.objects.select_related('module__material'), pk=pk)
        self.check_material_permission(lesson.module.material)

        prev_lesson = (
            Lesson.objects.filter(module=lesson.module, order__lt=lesson.order)
            .order_by('-order')
            .first()
        )
        if prev_lesson:
            with transaction.atomic():
                lesson.order, prev_lesson.order = prev_lesson.order, lesson.order
                lesson.save(update_fields=['order'])
                prev_lesson.save(update_fields=['order'])

        return redirect('editor:material_edit', slug=lesson.module.material.slug)


class EditorLessonMoveDownView(MaterialAuthorOrAdminMixin, View):
    """Перемещение урока ниже внутри своего модуля."""

    def post(self, request, pk, *args, **kwargs):
        lesson = get_object_or_404(Lesson.objects.select_related('module__material'), pk=pk)
        self.check_material_permission(lesson.module.material)

        next_lesson = (
            Lesson.objects.filter(module=lesson.module, order__gt=lesson.order)
            .order_by('order')
            .first()
        )
        if next_lesson:
            with transaction.atomic():
                lesson.order, next_lesson.order = next_lesson.order, lesson.order
                lesson.save(update_fields=['order'])
                next_lesson.save(update_fields=['order'])

        return redirect('editor:material_edit', slug=lesson.module.material.slug)


# =====================================================================
# Загрузка изображений из TinyMCE редактора
# =====================================================================

@csrf_exempt
def editor_upload_image(request):
    """Загрузка изображения педагогом через TinyMCE в директорию media/teachers/<user_id>/."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод запроса должен быть POST.'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация.'}, status=401)

    user_role = getattr(request.user, 'role', '')
    is_admin = getattr(request.user, 'is_administrator', False) or getattr(request.user, 'is_superuser', False)
    is_approved = getattr(request.user, 'is_approved', False)

    if (user_role not in ['teacher', 'admin'] and not is_admin) or (user_role == 'teacher' and not is_approved and not is_admin):
        return JsonResponse({'error': 'Доступно только подтвержденным педагогам и администраторам.'}, status=403)

    file_obj = request.FILES.get('file')
    if not file_obj:
        return JsonResponse({'error': 'Файл изображения не передан.'}, status=400)

    # Валидация расширения файла
    ext = Path(file_obj.name).suffix.lower()
    allowed_exts = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'}
    if ext not in allowed_exts:
        return JsonResponse({'error': f'Недопустимый формат файла {ext}.'}, status=400)

    try:
        user_folder = Path(settings.MEDIA_ROOT) / f"teachers/{request.user.id}"
        user_folder.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid4().hex}{ext}"
        destination_path = user_folder / filename

        with open(destination_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        media_url = settings.MEDIA_URL.rstrip('/')
        location = f"{media_url}/teachers/{request.user.id}/{filename}"
        return JsonResponse({'location': location})
    except Exception as exc:
        return JsonResponse({'error': f'Ошибка сохранения файла: {str(exc)}'}, status=400)

