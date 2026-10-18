from django.db import models


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
