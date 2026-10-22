from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя платформы KvantLearn."""

    ROLE_TEACHER = 'teacher'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_TEACHER, 'Педагог'),
        (ROLE_ADMIN, 'Администратор'),
    ]

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_TEACHER,
    )
    is_approved = models.BooleanField(
        'Подтвержден администратором',
        default=False,
        help_text='Педагог может работать в редакторе только после одобрения аккаунта.',
    )
    full_name = models.CharField(
        'ФИО или отображаемое имя',
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(
        'Дата регистрации',
        auto_now_add=True,
    )
    consent_personal_data = models.BooleanField(
        'Согласие на обработку ПДн',
        default=False,
        help_text='Факт дачи согласия на обработку персональных данных (152-ФЗ).',
    )
    consent_date = models.DateTimeField(
        'Дата и время дачи согласия',
        null=True,
        blank=True,
    )
    consent_version = models.CharField(
        'Версия документов согласия',
        max_length=20,
        blank=True,
        help_text='Версия политики и соглашения, с которой согласился пользователь (например, "1.0").',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        display = self.full_name or self.username
        return f"{display} ({self.get_role_display()})"

    @property
    def display_name(self):
        return self.full_name.strip() if self.full_name else self.username

    @property
    def is_teacher(self):
        return self.role == self.ROLE_TEACHER

    @property
    def is_administrator(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    def save(self, *args, **kwargs):
        # Суперпользователи Django всегда получают статус администратора и одобрение
        if self.is_superuser:
            self.role = self.ROLE_ADMIN
            self.is_approved = True
        super().save(*args, **kwargs)
