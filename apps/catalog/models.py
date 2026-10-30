from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def cyrillic_slugify(text: str) -> str:
    """Транслитерация кириллицы для красивых и валидных URL slug."""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    cleaned = ''
    for char in text.lower():
        cleaned += translit_map.get(char, char)
    return slugify(cleaned)


class Material(models.Model):
    """Учебный курс или материал в каталоге."""

    title = models.CharField('Название', max_length=255)
    slug = models.SlugField(
        'URL-идентификатор (slug)',
        max_length=255,
        unique=True,
        blank=True,
        help_text='Уникальный путь в URL, генерируется автоматически из названия при пустом значении.',
    )
    short_description = models.CharField('Краткое описание', max_length=300)
    cover_image = models.ImageField(
        'Обложка материала',
        upload_to='materials/covers/',
        blank=True,
    )
    direction = models.CharField(
        'Направление',
        max_length=50,
        choices=settings.DIRECTION_CHOICES,
        default='programming',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='Автор',
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=False,
        help_text='Неопубликованные материалы видны только автору и администраторам.',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Учебный материал'
        verbose_name_plural = 'Учебные материалы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog:material_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = cyrillic_slugify(self.title) or 'material'
            slug = base_slug
            counter = 1
            while Material.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_lessons_count(self):
        return Lesson.objects.filter(module__material=self).count()


class Module(models.Model):
    """Раздел или глава внутри учебного материала."""

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Материал',
    )
    title = models.CharField('Название модуля', max_length=255)
    order = models.PositiveIntegerField('Порядковый номер', default=1)

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.material.title} — {self.title}"


class Lesson(models.Model):
    """Урок внутри модуля учебного материала."""

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Модуль',
    )
    title = models.CharField('Название урока', max_length=255)
    order = models.PositiveIntegerField('Порядковый номер', default=1)
    content = models.TextField('Содержимое урока (HTML)', blank=True)
    image = models.ImageField(
        'Изображение к уроку',
        upload_to='lessons/images/',
        blank=True,
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.module.title} / {self.title}"

    def get_absolute_url(self):
        return reverse(
            'catalog:lesson_detail',
            kwargs={'slug': self.module.material.slug, 'pk': self.pk},
        )

