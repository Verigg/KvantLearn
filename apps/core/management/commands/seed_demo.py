from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser
from apps.catalog.models import Lesson, Material, Module
from apps.core.models import SiteSettings


class Command(BaseCommand):
    help = 'Заполняет базу данных демонстрационными данными для KvantLearn'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Начало заполнения демо-данных...'))

        # 1. Настройки сайта
        settings = SiteSettings.get_settings()
        settings.site_name = 'KvantLearn'
        settings.site_description = 'Каталог учебных материалов и практических уроков для кванторианцев по IT и современным технологиям.'
        settings.hero_title = 'Изучай IT и технологии в Кванториуме'
        settings.hero_subtitle = 'Доступные и структурированные учебные материалы, подготовленные наставниками ДТ «Кванториум». Выбирай направление, изучай теорию и создавай свои инженерные проекты!'
        settings.contact_email = 'kvantlearn@kvantorium.ru'
        settings.footer_text = 'ДТ «Кванториум» — современная экосистема детского научно-технического творчества.'
        settings.save()
        self.stdout.write(self.style.SUCCESS('✓ Настройки сайта обновлены.'))

        # 2. Пользователи
        # Администратор
        admin_user, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'role': CustomUser.ROLE_ADMIN,
                'is_approved': True,
                'is_staff': True,
                'is_superuser': True,
                'full_name': 'Главный администратор',
                'email': 'admin@kvantorium.ru',
            },
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Создан суперпользователь: admin / admin123'))
        else:
            self.stdout.write('Пользователь admin уже существует.')

        # Подтвержденный педагог
        teacher_user, created = CustomUser.objects.get_or_create(
            username='teacher_mikhail',
            defaults={
                'role': CustomUser.ROLE_TEACHER,
                'is_approved': True,
                'full_name': 'Михаил Сергеевич Ковалёв (IT-квантум)',
                'email': 'mikhail@kvantorium.ru',
            },
        )
        if created:
            teacher_user.set_password('teacher123')
            teacher_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Создан педагог: teacher_mikhail / teacher123'))
        else:
            self.stdout.write('Пользователь teacher_mikhail уже существует.')

        # Новый неподтвержденный педагог для демонстрации функционала одобрения
        pending_user, created = CustomUser.objects.get_or_create(
            username='teacher_anna',
            defaults={
                'role': CustomUser.ROLE_TEACHER,
                'is_approved': False,
                'full_name': 'Анна Владимировна Смирнова (VR/AR-квантум)',
                'email': 'anna@kvantorium.ru',
            },
        )
        if created:
            pending_user.set_password('teacher123')
            pending_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Создан неподтвержденный педагог: teacher_anna / teacher123'))

        # 3. Материал 1: Python
        mat1, created = Material.objects.get_or_create(
            slug='osnovy-python-dlya-nachinayushchikh',
            defaults={
                'title': 'Основы Python для начинающих разработчиков',
                'short_description': 'Пошаговый практический курс по языку Python для кванторианцев: от первой строчки кода до написания собственных скриптов и алгоритмов.',
                'direction': 'programming',
                'author': teacher_user,
                'is_published': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Создан материал: {mat1.title}'))

        # Модуль 1 в Материале 1
        mod1, _ = Module.objects.get_or_create(
            material=mat1,
            title='Модуль 1. Знакомство со средой разработки и синтаксисом',
            defaults={'order': 1},
        )

        # Урок 1 в Модуле 1
        lesson1_content = """# Первые шаги в Python

Добро пожаловать в вводный урок по изучению Python! Python — один из самых популярных, выразительных и дружелюбных языков программирования в мире.

## Почему именно Python?

- **Простой и лаконичный синтаксис**: код на Python читается практически как обычный английский текст.
- **Огромное сообщество**: миллионы готовых библиотек для машинного обучения, веб-разработки, робототехники и автоматизации.
- **Кроссплатформенность**: ваш код будет одинаково работать на Windows, macOS и Linux.

## Первая программа: Hello, World!

Традиционно знакомство с любым языком начинается с вывода приветствия:

```python
# Наша первая строка кода
print("Привет, Кванториум!")
```

### Как запустить программу?
1. Откройте терминал или командную строку.
2. Введите команду:
   ```bash
   python main.py
   ```
3. Вы увидите приветственное сообщение на экране!

> **Совет наставника:** Не бойтесь делать ошибки! Каждая ошибка в терминале — это подсказка интерпретатора о том, что именно нужно исправить.
"""
        Lesson.objects.get_or_create(
            module=mod1,
            title='Урок 1. Установка и запуск первой программы',
            defaults={
                'order': 1,
                'content_type': Lesson.TYPE_MARKDOWN,
                'content': lesson1_content,
                'video_url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8',
            },
        )

        # Урок 2 в Модуле 1
        lesson2_content = """# Переменные и основные типы данных

В программировании переменная — это поименованная ячейка памяти компьютера, в которой сохраняется значение для дальнейшей работы.

## Основные базовые типы данных в Python

| Тип данных | Обозначение | Пример значения | Пояснение |
| :--- | :--- | :--- | :--- |
| **Целое число** | `int` | `42`, `-10`, `0` | Для подсчета количества предметов, возраста |
| **Вещественное число** | `float` | `3.14`, `-0.5` | Дробные величины, координаты, измерения датчиков |
| **Строка** | `str` | `"Кванториум"` | Текстовая информация |
| **Булев тип** | `bool` | `True`, `False` | Логические флаги «Да / Нет» |

## Пример создания переменных в коде

```python
kvantum_name = "IT-Квантум"
students_count = 14
lesson_duration_hours = 1.5
is_active = True

print(f"В квантуме {kvantum_name} обучаются {students_count} учеников.")
```

## Практическое задание

Попробуйте создать переменные для своего имени, возраста и любимого направления технологий, а затем вывести их с помощью форматированной строки `f-string`.
"""
        Lesson.objects.get_or_create(
            module=mod1,
            title='Урок 2. Переменные и типы данных',
            defaults={
                'order': 2,
                'content_type': Lesson.TYPE_MARKDOWN,
                'content': lesson2_content,
            },
        )

        # 4. Материал 2: Робототехника
        mat2, created = Material.objects.get_or_create(
            slug='robototekhnika-i-mikrokontrollery-arduino',
            defaults={
                'title': 'Робототехника и микроконтроллеры Arduino',
                'short_description': 'Курс по проектированию умных электронных устройств: схемы подключения, цифровые и аналоговые порты, датчики и написание прошивок на C++.',
                'direction': 'robotics',
                'author': teacher_user,
                'is_published': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Создан материал: {mat2.title}'))

        # Модуль 1 в Материале 2
        mod2, _ = Module.objects.get_or_create(
            material=mat2,
            title='Модуль 1. Основы схемотехники и плата Arduino Uno',
            defaults={'order': 1},
        )

        # Урок 1 в Модуле 2
        lesson3_content = """# Архитектура Arduino Uno и макетная плата

Платформа Arduino — это удобный инструмент для быстрого прототипирования электронных систем.

## Что находится на плате Arduino Uno?

- **Микроконтроллер ATmega328P** — сердце платы, выполняющее команды прошивки.
- **14 цифровых пинов (Digital I/O)** — пины с 0 по 13 для приема и передачи логических сигналов (HIGH/LOW).
- **6 аналоговых входов (A0 - A5)** — позволяют измерять напряжение от 0 до 5 вольт (например, с фоторезистора или терморезистора).
- **Стабилизатор питания и разъем USB** — для подачи напряжения и загрузки скетчей из Arduino IDE.

```cpp
void setup() {
  // Настройка цифрового пина 13 на режим вывода
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH); // Включить светодиод
  delay(1000);            // Ждать 1 секунду
  digitalWrite(13, LOW);  // Выключить светодиод
  delay(1000);            // Ждать 1 секунду
}
```

Всегда проверяйте правильность полярности электронных компонентов перед подачей питания на плату!
"""
        Lesson.objects.get_or_create(
            module=mod2,
            title='Урок 1. Архитектура контроллера и скетч «Мигающий светодиод»',
            defaults={
                'order': 1,
                'content_type': Lesson.TYPE_MARKDOWN,
                'content': lesson3_content,
                'video_url': 'https://www.youtube.com/watch?v=09zf38F5iZ0',
            },
        )

        # Урок 2 в Модуле 2
        lesson4_content = """# Подключение кнопки и обработка дребезга контактов

Кнопка — это базовый датчик дискретного ввода. Однако механические контакты кнопки не замыкаются мгновенно.

## Схема с подтягивающим резистором (Pull-up)

Чтобы избежать случайных наводок (плавающего состояния пина), вход должен быть подтянут к питанию 5V или к земле (GND). В микроконтроллерах ATmega328P уже есть встроенные подтягивающие резисторы:

```cpp
const int BUTTON_PIN = 2;
const int LED_PIN = 13;

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  int buttonState = digitalRead(BUTTON_PIN);
  if (buttonState == LOW) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
}
```

Обратите внимание: при использовании `INPUT_PULLUP` ненажатая кнопка возвращает `HIGH`, а при нажатии на кнопку — замкнута на землю и возвращает `LOW`.
"""
        Lesson.objects.get_or_create(
            module=mod2,
            title='Урок 2. Подключение кнопки и обработка дискретных сигналов',
            defaults={
                'order': 2,
                'content_type': Lesson.TYPE_MARKDOWN,
                'content': lesson4_content,
            },
        )

        self.stdout.write(self.style.SUCCESS('✓ Демо-данные успешно созданы!'))
