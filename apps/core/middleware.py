import re
from django.utils import timezone
from apps.core.models import PageVisit
from apps.catalog.models import Lesson, Material


class PageVisitMiddleware:
    """
    Middleware для неблокирующей фиксации посещений публичных страниц каталога и уроков.
    Исключает запросы поисковых ботов, служебные разделы (/editor/, /admin/, /static/, /media/)
    и фиксирует только GET-запросы с привязкой к сессиям, материалам и педагогам.
    """

    EXCLUDED_PREFIXES = ('/editor/', '/admin/', '/static/', '/media/')
    BOT_KEYWORDS = ('bot', 'crawler', 'spider', 'facebookexternalhit', 'slurp')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Выполняем логирование посещения в изолированном блоке
        try:
            self._log_visit(request, response)
        except Exception:
            # Ошибка логирования ни при каких обстоятельствах не нарушает ответ сервера
            pass

        return response

    def _log_visit(self, request, response):
        # Записываем только GET-запросы
        if request.method != 'GET':
            return

        # Не логируем ошибочные ответы сервера (5xx)
        if response.status_code >= 500:
            return

        path = request.path

        # Минимальный фильтр ботов по User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(bot_kw in user_agent for bot_kw in self.BOT_KEYWORDS):
            return

        # Исключаем служебные разделы
        if any(path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES):
            return

        # Логируем только публичные страницы каталога
        if not (path.startswith('/catalog') or path.startswith('/materials')):
            return

        # Определение ключа сессии
        session_key = ''
        if hasattr(request, 'session'):
            if not request.session.session_key:
                try:
                    request.session.save()
                except Exception:
                    pass
            session_key = request.session.session_key or ''

        material = None
        teacher = None

        # Проверка 1: Страница урока (например, /catalog/lesson/<pk>/, /catalog/<slug>/lessons/<pk>/, /materials/<slug>/lessons/<pk>/)
        lesson_match = re.search(
            r'/(?:catalog/lesson|catalog/[^/]+/lessons|materials/[^/]+/lessons)/(?P<pk>\d+)/?',
            path
        )
        if lesson_match:
            try:
                lesson_pk = int(lesson_match.group('pk'))
                lesson = (
                    Lesson.objects.select_related('module__material', 'module__material__author')
                    .filter(pk=lesson_pk)
                    .first()
                )
                if lesson and lesson.module and lesson.module.material:
                    material = lesson.module.material
                    teacher = material.author
            except Exception:
                pass
        else:
            # Проверка 2: Страница материала (например, /catalog/material/<slug>/, /catalog/<slug>/, /materials/<slug>/)
            mat_match = re.search(
                r'/(?:catalog/material|catalog|materials)/(?P<slug>[-\w]+)/?',
                path
            )
            if mat_match:
                slug = mat_match.group('slug')
                if slug not in ('material', 'lesson', 'lessons', 'editor'):
                    try:
                        mat = Material.objects.select_related('author').filter(slug=slug).first()
                        if mat:
                            material = mat
                            teacher = mat.author
                    except Exception:
                        pass

        # Создание записи в базе данных
        PageVisit.objects.create(
            path=path,
            material=material,
            teacher=teacher,
            session_key=session_key,
            timestamp=timezone.now(),
        )
