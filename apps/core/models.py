from django.db import models
from django.utils import timezone


class SiteSettings(models.Model):
    """Глобальные настройки сайта (паттерн Singleton)."""

    site_name = models.CharField(
        'Название сайта',
        max_length=150,
        default='KvantLearn',
    )
    site_description = models.TextField(
        'Описание сайта',
        blank=True,
        default='Каталог учебных материалов и практических уроков для кванторианцев по IT и современным технологиям.',
    )
    hero_title = models.CharField(
        'Главный заголовок (Hero)',
        max_length=255,
        blank=True,
        default='Изучай IT и технологии в Кванториуме',
    )
    hero_subtitle = models.TextField(
        'Подзаголовок (Hero)',
        blank=True,
        default='Доступные и структурированные учебные материалы, написанные педагогами ДТ «Кванториум». Выбирай направление и прокачивай свои навыки!',
    )
    contact_email = models.EmailField(
        'Контактный email',
        blank=True,
        default='kvantlearn@example.com',
    )
    footer_text = models.CharField(
        'Текст в подвале (Footer)',
        max_length=255,
        blank=True,
        default='ДТ «Кванториум» — современная экосистема детского научно-технического творчества.',
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return f"Настройки: {self.site_name}"

    @classmethod
    def get_settings(cls):
        """Возвращает единственный экземпляр настроек или создает его по умолчанию."""
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj

    def save(self, *args, **kwargs):
        # Гарантируем единственный объект в БД с pk=1
        self.pk = 1
        super().save(*args, **kwargs)


# Обоснование выбора apps/core для модели PageVisit:
# Модель PageVisit размещена в apps/core, так как она агрегирует общесистемную аналитику,
# трафик и аудит посещений всей платформы KvantLearn (включая будущие расширения страниц),
# относится к административному функционалу управления сайтом (core),
# и исключает зацепление доменной модели учебных курсов (apps/catalog) с логикой логирования запросов.
class PageVisit(models.Model):
    """Журнал посещений публичных страниц каталога и уроков."""

    path = models.CharField(
        'URL путь',
        max_length=500,
    )
    material = models.ForeignKey(
        'catalog.Material',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='visit_stats',
        verbose_name='Материал',
    )
    teacher = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='visit_stats',
        verbose_name='Педагог',
    )
    session_key = models.CharField(
        'Ключ сессии',
        max_length=100,
        blank=True,
    )
    timestamp = models.DateTimeField(
        'Время посещения',
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Посещение страницы'
        verbose_name_plural = 'Посещения страниц'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['material', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.path} ({self.timestamp:%Y-%m-%d %H:%M})"

