from django.test import Client, TestCase
from django.urls import reverse
from apps.accounts.models import CustomUser


class PersonalDataConsentTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_requires_consent(self):
        """Регистрация без согласия на обработку ПДн должна завершаться ошибкой валидации."""
        response = self.client.post(
            reverse('accounts:register'),
            data={
                'username': 'new_teacher_no_consent',
                'full_name': 'Петров Петр Петрович',
                'password1': 'StrongPass123',
                'password2': 'StrongPass123',
                # consent не передан
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Необходимо согласие на обработку персональных данных')
        self.assertFalse(CustomUser.objects.filter(username='new_teacher_no_consent').exists())

    def test_registration_with_consent_saves_metadata(self):
        """При согласии фиксируются consent_personal_data=True, consent_date и версия '1.0'."""
        response = self.client.post(
            reverse('accounts:register'),
            data={
                'username': 'new_teacher_with_consent',
                'full_name': 'Сидорова Светлана Михайловна',
                'password1': 'StrongPass123',
                'password2': 'StrongPass123',
                'consent': True,
            },
        )
        # Редирект на страницу ожидания подтверждения
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('accounts:pending'))

        user = CustomUser.objects.get(username='new_teacher_with_consent')
        self.assertTrue(user.consent_personal_data)
        self.assertIsNotNone(user.consent_date)
        self.assertEqual(user.consent_version, '1.0')
        self.assertFalse(user.is_approved)

    def test_privacy_and_terms_pages_accessible_anonymously(self):
        """Страницы /privacy/ и /terms/ публично доступны без авторизации."""
        res_privacy = self.client.get(reverse('privacy'))
        self.assertEqual(res_privacy.status_code, 200)
        self.assertContains(res_privacy, 'Политика конфиденциальности')
        self.assertContains(res_privacy, '152-ФЗ')

        res_terms = self.client.get(reverse('terms'))
        self.assertEqual(res_terms.status_code, 200)
        self.assertContains(res_terms, 'Пользовательское соглашение')

    def test_registration_page_contains_legal_links_and_checkbox(self):
        """Форма регистрации содержит чекбокс, ссылки на документы и атрибут disabled у кнопки."""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="consent"')
        self.assertContains(response, 'id="register-btn"')
        self.assertContains(response, 'disabled')
        self.assertContains(response, reverse('privacy'))
        self.assertContains(response, reverse('terms'))
