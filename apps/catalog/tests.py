from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import CustomUser
from apps.catalog.models import Material, Module, Lesson


class CatalogAndEditorTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Admin
        self.admin = CustomUser.objects.create_superuser(
            username='test_admin',
            password='password123',
            role=CustomUser.ROLE_ADMIN,
            is_approved=True,
        )
        # Approved teacher
        self.teacher1 = CustomUser.objects.create_user(
            username='teacher1',
            password='password123',
            role=CustomUser.ROLE_TEACHER,
            is_approved=True,
            full_name='Учитель Первый',
        )
        # Another approved teacher
        self.teacher2 = CustomUser.objects.create_user(
            username='teacher2',
            password='password123',
            role=CustomUser.ROLE_TEACHER,
            is_approved=True,
            full_name='Учитель Второй',
        )
        # Pending teacher
        self.pending_teacher = CustomUser.objects.create_user(
            username='pending_teacher',
            password='password123',
            role=CustomUser.ROLE_TEACHER,
            is_approved=False,
            full_name='Ожидающий Учитель',
        )

        # Materials
        self.published_mat = Material.objects.create(
            title='Опубликованный курс',
            slug='published-course',
            short_description='Краткое описание курса',
            direction='programming',
            author=self.teacher1,
            is_published=True,
        )
        self.module1 = Module.objects.create(
            material=self.published_mat,
            title='Модуль 1',
            order=1,
        )
        self.lesson1 = Lesson.objects.create(
            module=self.module1,
            title='Урок 1',
            order=1,
            content_type=Lesson.TYPE_MARKDOWN,
            content='# Заголовок\n\n```python\nprint("тест")\n```',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        )

        self.draft_mat = Material.objects.create(
            title='Черновик курса',
            slug='draft-course',
            short_description='Черновой курс',
            direction='robotics',
            author=self.teacher1,
            is_published=False,
        )

    def test_public_views(self):
        # Главная страница
        res = self.client.get(reverse('core:home'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Опубликованный курс')

        # Каталог
        res = self.client.get(reverse('catalog:material_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Опубликованный курс')
        self.assertNotContains(res, 'Черновик курса')

        # Просмотр опубликованного материала
        res = self.client.get(reverse('catalog:material_detail', kwargs={'slug': 'published-course'}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Модуль 1')

        # Просмотр урока
        res = self.client.get(reverse('catalog:lesson_detail', kwargs={'slug': 'published-course', 'pk': self.lesson1.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Урок 1')

        # Просмотр черновика анонимом -> 404
        res = self.client.get(reverse('catalog:material_detail', kwargs={'slug': 'draft-course'}))
        self.assertEqual(res.status_code, 404)

    def test_editor_access_permissions(self):
        # Аноним пытается войти в редактор -> редирект на логин
        res = self.client.get(reverse('editor:material_list'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('accounts:login'), res.url)

        # Неподтвержденный педагог -> редирект на pending
        self.client.login(username='pending_teacher', password='password123')
        res = self.client.get(reverse('editor:material_list'))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('accounts:pending'))
        self.client.logout()

        # Подтвержденный педагог видит только свои материалы
        self.client.login(username='teacher1', password='password123')
        res = self.client.get(reverse('editor:material_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Опубликованный курс')
        self.assertContains(res, 'Черновик курса')

        # Педагог 2 пытается редактировать чужой материал -> 403
        self.client.logout()
        self.client.login(username='teacher2', password='password123')
        res = self.client.get(reverse('editor:material_edit', kwargs={'slug': 'published-course'}))
        self.assertEqual(res.status_code, 403)

        # Педагог 2 не имеет доступа к настройкам админа -> 403
        res = self.client.get(reverse('core:settings'))
        self.assertEqual(res.status_code, 403)
        self.client.logout()

        # Админ имеет доступ к настройкам и видит все
        self.client.login(username='test_admin', password='password123')
        res = self.client.get(reverse('core:settings'))
        self.assertEqual(res.status_code, 200)
        res = self.client.get(reverse('core:users_list'))
        self.assertEqual(res.status_code, 200)
