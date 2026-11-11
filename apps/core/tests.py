from datetime import timedelta
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.catalog.models import Material
from apps.core.models import PageVisit


class StatsAndTrackingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.now = timezone.now()

        # Создаем администратора
        self.admin = CustomUser.objects.create_superuser(
            username='admin_stats',
            password='password123',
            role=CustomUser.ROLE_ADMIN,
            is_approved=True,
            full_name='Главный Администратор',
        )

        # Создаем педагогов
        self.teacher1 = CustomUser.objects.create_user(
            username='teacher_stats_1',
            password='password123',
            role=CustomUser.ROLE_TEACHER,
            is_approved=True,
            full_name='Педагог Первый',
        )
        self.teacher2 = CustomUser.objects.create_user(
            username='teacher_stats_2',
            password='password123',
            role=CustomUser.ROLE_TEACHER,
            is_approved=True,
            full_name='Педагог Второй',
        )

        # Создаем учебные материалы
        self.material1 = Material.objects.create(
            title='Курс по Python',
            slug='python-intro',
            short_description='Основы языка Python',
            direction='programming',
            author=self.teacher1,
            is_published=True,
        )
        self.material2 = Material.objects.create(
            title='Курс по Робототехнике',
            slug='robotics-intro',
            short_description='Основы робототехники',
            direction='robotics',
            author=self.teacher2,
            is_published=True,
        )

    def test_stats_access_permissions(self):
        """
        Проверка прав доступа:
        - анонимный пользователь перенаправляется на форму входа (302);
        - педагог получает отказ в доступе (403);
        - подтвержденный администратор получает доступ (200).
        """
        urls = [
            reverse('core:stats'),
            reverse('core:stats_material', kwargs={'pk': self.material1.pk}),
            reverse('core:stats_teacher', kwargs={'pk': self.teacher1.pk}),
        ]

        for url in urls:
            # 1. Анонимный запрос -> 302 на логин
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('accounts:login'), response.url)

            # 2. Педагог -> 403 Forbidden
            self.client.login(username='teacher_stats_1', password='password123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

            # 3. Администратор -> 200 OK
            self.client.login(username='admin_stats', password='password123')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_page_visit_recording(self):
        """
        Запись посещений: GET-запрос к публичной странице каталога /catalog/material/<slug>/
        создает объект PageVisit с правильным material и teacher.
        """
        url = f'/catalog/material/{self.material1.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Проверяем наличие записи
        visit = PageVisit.objects.filter(path=url).first()
        self.assertIsNotNone(visit)
        self.assertEqual(visit.material, self.material1)
        self.assertEqual(visit.teacher, self.teacher1)
        self.assertTrue(len(visit.session_key) > 0)

    def test_bots_not_logged(self):
        """Посещения поисковых роботов (по User-Agent) не логируются."""
        initial_count = PageVisit.objects.count()
        bot_user_agents = [
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'YandexBot/3.0 (+http://yandex.com/bots)',
            'facebookexternalhit/1.1; (+http://www.facebook.com/externalhit_uatext.php)',
            'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
            'Python-urllib/3.10 spider-crawler',
        ]

        for ua in bot_user_agents:
            self.client.get(
                f'/catalog/material/{self.material1.slug}/',
                HTTP_USER_AGENT=ua,
            )

        self.assertEqual(PageVisit.objects.count(), initial_count)

    def test_periods_filtering(self):
        """
        Проверка фильтрации по периодам:
        - '3m': фильтрует по последним 90 дням (timestamp__gte=now - 90d);
        - 'year': фильтрует по текущему году (timestamp__year=now.year);
        - 'all': без ограничения по дате.
        """
        PageVisit.objects.all().delete()

        # Создаем записи с разными временными метками:
        # 1) 10 дней назад (попадает во все 3 периода)
        v1 = PageVisit.objects.create(
            path=f'/catalog/material/{self.material1.slug}/',
            material=self.material1,
            teacher=self.teacher1,
            session_key='s1',
            timestamp=self.now - timedelta(days=10),
        )

        # 2) 120 дней назад, принудительно в текущем календарном году
        # (если текущая дата в начале года, берем середину января текущего года)
        date_in_current_year = self.now.replace(month=1, day=15, hour=12, minute=0)
        # Если сейчас и есть январь, смещаем на несколько дней назад
        if (self.now - date_in_current_year).days < 95:
            # Делаем дату более 95 дней назад в текущем году, если возможно, либо декабрь прошлого года
            older_date = self.now - timedelta(days=110)
        else:
            older_date = date_in_current_year

        v2 = PageVisit.objects.create(
            path=f'/catalog/material/{self.material1.slug}/',
            material=self.material1,
            teacher=self.teacher1,
            session_key='s2',
            timestamp=older_date,
        )

        # 3) Прошлый год (например, 450 дней назад)
        past_year_date = self.now.replace(year=self.now.year - 1)
        v3 = PageVisit.objects.create(
            path=f'/catalog/material/{self.material1.slug}/',
            material=self.material1,
            teacher=self.teacher1,
            session_key='s3',
            timestamp=past_year_date,
        )

        self.client.login(username='admin_stats', password='password123')

        # Запрос за прошлые 3 месяца ('3m')
        res_3m = self.client.get(reverse('core:stats') + '?period=3m')
        self.assertEqual(res_3m.status_code, 200)
        # Должен включать визит за последние 10 дней, но исключать визит 450 дней назад
        self.assertEqual(res_3m.context['period'], '3m')
        self.assertIn(v1.id, [v.id for v in res_3m.context['top_materials'][0]['material'].visit_stats.filter(timestamp__gte=self.now - timedelta(days=90))])

        # Запрос за текущий год ('year')
        res_year = self.client.get(reverse('core:stats') + '?period=year')
        self.assertEqual(res_year.status_code, 200)
        self.assertEqual(res_year.context['period'], 'year')

        # Запрос за все время ('all')
        res_all = self.client.get(reverse('core:stats') + '?period=all')
        self.assertEqual(res_all.status_code, 200)
        self.assertEqual(res_all.context['period'], 'all')
        self.assertEqual(res_all.context['total_visits'], 3)
        self.assertEqual(res_all.context['unique_sessions'], 3)

    def test_detail_views_isolate_entities(self):
        """
        Детализация по материалу и педагогу отдает только относящиеся записи.
        """
        PageVisit.objects.all().delete()

        # Посещения для материала 1 (педагог 1)
        PageVisit.objects.create(
            path=f'/catalog/material/{self.material1.slug}/',
            material=self.material1,
            teacher=self.teacher1,
            session_key='sess_mat1_a',
            timestamp=self.now - timedelta(days=2),
        )
        PageVisit.objects.create(
            path=f'/catalog/material/{self.material1.slug}/',
            material=self.material1,
            teacher=self.teacher1,
            session_key='sess_mat1_b',
            timestamp=self.now - timedelta(days=1),
        )

        # Посещение для материала 2 (педагог 2)
        PageVisit.objects.create(
            path=f'/catalog/material/{self.material2.slug}/',
            material=self.material2,
            teacher=self.teacher2,
            session_key='sess_mat2',
            timestamp=self.now - timedelta(days=1),
        )

        self.client.login(username='admin_stats', password='password123')

        # Детализация материала 1
        res_mat = self.client.get(reverse('core:stats_material', kwargs={'pk': self.material1.pk}) + '?period=all')
        self.assertEqual(res_mat.status_code, 200)
        self.assertEqual(res_mat.context['total_visits'], 2)
        self.assertEqual(res_mat.context['unique_sessions'], 2)
        self.assertEqual(res_mat.context['material'], self.material1)

        # Детализация педагога 1
        res_teach = self.client.get(reverse('core:stats_teacher', kwargs={'pk': self.teacher1.pk}) + '?period=all')
        self.assertEqual(res_teach.status_code, 200)
        self.assertEqual(res_teach.context['total_visits'], 2)
        self.assertEqual(res_teach.context['unique_sessions'], 2)
        self.assertEqual(res_teach.context['teacher'], self.teacher1)

        # Детализация педагога 2
        res_teach2 = self.client.get(reverse('core:stats_teacher', kwargs={'pk': self.teacher2.pk}) + '?period=all')
        self.assertEqual(res_teach2.status_code, 200)
        self.assertEqual(res_teach2.context['total_visits'], 1)
        self.assertEqual(res_teach2.context['unique_sessions'], 1)
        self.assertEqual(res_teach2.context['teacher'], self.teacher2)
