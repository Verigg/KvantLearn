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

        # Урок 1 в Модуле 1 (Rich text HTML)
        lesson1_content = """<h2>Первые шаги в Python</h2>
<p>Добро пожаловать в вводный урок по изучению Python! Python — один из самых популярных, выразительных и дружелюбных языков программирования в мире.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 1.5rem 0; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
  <iframe src="https://www.youtube.com/embed/kqtD5dpn9C8" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

<h3>Почему именно Python?</h3>
<ul>
  <li><strong>Простой и лаконичный синтаксис:</strong> код на Python читается практически как обычный английский текст.</li>
  <li><strong>Огромное сообщество:</strong> тысячи готовых библиотек для машинного обучения, веб-разработки, робототехники и автоматизации.</li>
  <li><strong>Кроссплатформенность:</strong> ваш код будет одинаково работать на Windows, macOS и Linux.</li>
</ul>

<h3>Первая программа: Hello, World!</h3>
<p>Традиционно знакомство с любым языком начинается с вывода приветствия:</p>
<pre><code class="language-python"># Наша первая строка кода
print("Привет, Кванториум!")
</code></pre>

<h3>Как запустить программу?</h3>
<ol>
  <li>Откройте терминал или командную строку в вашей среде разработки.</li>
  <li>Введите команду: <code>python main.py</code></li>
  <li>Вы увидите приветственное сообщение на экране!</li>
</ol>

<blockquote>
  <p><strong>Совет наставника:</strong> Не бойтесь делать ошибки! Каждая ошибка в терминале — это подсказка интерпретатора о том, что именно нужно исправить в логике программы.</p>
</blockquote>
"""
        lesson1, l1_created = Lesson.objects.get_or_create(
            module=mod1,
            title='Урок 1. Установка и запуск первой программы',
            defaults={
                'order': 1,
                'content': lesson1_content,
            },
        )
        if not l1_created:
            lesson1.content = lesson1_content
            lesson1.save()

        # Урок 2 в Модуле 1 (Rich text HTML)
        lesson2_content = """<h2>Переменные и основные типы данных</h2>
<p>В программировании переменная — это поименованная ячейка памяти компьютера, в которой сохраняется значение для дальнейшей работы.</p>

<h3>Основные базовые типы данных в Python</h3>
<table style="width: 100%; border-collapse: collapse; margin: 1.5rem 0;">
  <thead>
    <tr style="background-color: #f1f5f9; text-align: left;">
      <th style="padding: 10px 14px; border: 1px solid #e2e8f0;">Тип данных</th>
      <th style="padding: 10px 14px; border: 1px solid #e2e8f0;">Обозначение</th>
      <th style="padding: 10px 14px; border: 1px solid #e2e8f0;">Пример значения</th>
      <th style="padding: 10px 14px; border: 1px solid #e2e8f0;">Пояснение</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><strong>Целое число</strong></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><code>int</code></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">42, -10, 0</td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">Для подсчета количества предметов, возраста</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><strong>Вещественное число</strong></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><code>float</code></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">3.14, -0.5</td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">Дробные величины, координаты, измерения датчиков</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><strong>Строка</strong></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><code>str</code></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">"Кванториум"</td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">Текстовая информация</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><strong>Булев тип</strong></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;"><code>bool</code></td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">True, False</td>
      <td style="padding: 10px 14px; border: 1px solid #e2e8f0;">Логические флаги «Да / Нет»</td>
    </tr>
  </tbody>
</table>

<h3>Пример создания переменных в коде</h3>
<pre><code class="language-python">kvantum_name = "IT-Квантум"
students_count = 14
lesson_duration_hours = 1.5
is_active = True

print(f"В квантуме {kvantum_name} обучаются {students_count} учеников.")
</code></pre>

<h3>Практическое задание</h3>
<p>Попробуйте создать переменные для своего имени, возраста и любимого направления технологий, а затем вывести их с помощью форматированной строки <code>f-string</code>.</p>
"""
        lesson2, l2_created = Lesson.objects.get_or_create(
            module=mod1,
            title='Урок 2. Переменные и типы данных',
            defaults={
                'order': 2,
                'content': lesson2_content,
            },
        )
        if not l2_created:
            lesson2.content = lesson2_content
            lesson2.save()

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

        # Урок 1 в Модуле 2 (Rich text HTML)
        lesson3_content = """<h2>Архитектура Arduino Uno и макетная плата</h2>
<p>Платформа Arduino — это удобный инструмент для быстрого прототипирования электронных систем и робототехники.</p>

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 1.5rem 0; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
  <iframe src="https://www.youtube.com/embed/09zf38F5iZ0" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

<h3>Что находится на плате Arduino Uno?</h3>
<ul>
  <li><strong>Микроконтроллер ATmega328P:</strong> сердце платы, выполняющее команды прошивки.</li>
  <li><strong>14 цифровых пинов (Digital I/O):</strong> пины с 0 по 13 для приема и передачи логических сигналов (HIGH/LOW).</li>
  <li><strong>6 аналоговых входов (A0 - A5):</strong> позволяют измерять напряжение от 0 до 5 вольт (например, с фоторезистора или терморезистора).</li>
  <li><strong>Стабилизатор питания и разъем USB:</strong> для подачи напряжения и загрузки скетчей из Arduino IDE.</li>
</ul>

<h3>Скетч «Мигающий светодиод»</h3>
<pre><code class="language-cpp">void setup() {
  // Настройка цифрового пина 13 на режим вывода
  pinMode(13, OUTPUT);
}

void loop() {
  digitalWrite(13, HIGH); // Включить светодиод
  delay(1000);            // Ждать 1 секунду
  digitalWrite(13, LOW);  // Выключить светодиод
  delay(1000);            // Ждать 1 секунду
}
</code></pre>

<blockquote>
  <p><strong>Важно:</strong> Всегда проверяйте правильность полярности электронных компонентов (анод/катод светодиода) перед подачей питания на плату!</p>
</blockquote>
"""
        lesson3, l3_created = Lesson.objects.get_or_create(
            module=mod2,
            title='Урок 1. Архитектура контроллера и скетч «Мигающий светодиод»',
            defaults={
                'order': 1,
                'content': lesson3_content,
            },
        )
        if not l3_created:
            lesson3.content = lesson3_content
            lesson3.save()

        # Урок 2 в Модуле 2 (Rich text HTML)
        lesson4_content = """<h2>Подключение кнопки и обработка дребезга контактов</h2>
<p>Кнопка — это базовый датчик дискретного ввода. Однако механические контакты кнопки не замыкаются мгновенно, что может вызывать ложные срабатывания.</p>

<h3>Схема с подтягивающим резистором (Pull-up)</h3>
<p>Чтобы избежать случайных наводок (плавающего состояния пина), вход должен быть подтянут к питанию 5V или к земле (GND). В микроконтроллерах ATmega328P уже есть встроенные программные подтягивающие резисторы:</p>

<pre><code class="language-cpp">const int BUTTON_PIN = 2;
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
</code></pre>

<p>Обратите внимание: при использовании <code>INPUT_PULLUP</code> ненажатая кнопка возвращает <code>HIGH</code>, а при нажатии на кнопку — замкнута на землю и возвращает <code>LOW</code>.</p>
"""
        lesson4, l4_created = Lesson.objects.get_or_create(
            module=mod2,
            title='Урок 2. Подключение кнопки и обработка дискретных сигналов',
            defaults={
                'order': 2,
                'content': lesson4_content,
            },
        )
        if not l4_created:
            lesson4.content = lesson4_content
            lesson4.save()

        self.stdout.write(self.style.SUCCESS('✓ Демо-данные успешно созданы в формате Rich Text!'))
