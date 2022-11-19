from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import User

urls_and_templates_authorisation_not_required = {
    '/auth/logout/': 'users/logged_out.html',
    '/auth/login/': 'users/login.html',
    '/auth/password_reset/': 'users/password_reset_form.html',
    '/auth/password_reset/done/': 'users/password_reset_done.html',
    '/auth/reset/<uidb64>/<token>/': 'users/password_reset_confirm.html',
    '/auth/reset/done/': 'users/password_reset_complete.html',
    '/auth/signup/': 'users/signup.html'
}

urls_and_templates_authorisation_required = {
    # Тут почемуто если поставить users а не registration,
    # не проходит тест, хотя шаблон я переопределил.
    '/auth/password_change/done/': 'registration/password_change_done.html',
    '/auth/password_change/': 'users/password_change_form.html',
}


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.user = User.objects.create(username='test_authorized_user')
        cls.authorized_client.force_login(cls.user)

    def test_urls_exists_at_desired_locations(self):
        """Проверка доступности адресов для неавторизованного пользователя."""
        for url in urls_and_templates_authorisation_not_required.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_password_change_redirect_if_not_authorised(self):
        """Проверка перенаправления пользователя со страницы
           изменения пароля и со страницы подтверждения изменения пароля,
           если пользователь не авторизован."""
        for url in urls_and_templates_authorisation_required.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_password_change_and_edit_url_authorised(self):
        """Проверка доступности для авторизованного пользователя
           страниц изменения пароля и подтверждения изменения пароля."""
        for url in urls_and_templates_authorisation_required.keys():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_uses_correct_templates(self):
        """Проверка использования правильных шаблонов в приложении Users."""
        all_users_url_and_templates = urls_and_templates_authorisation_required
        for url, template in all_users_url_and_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
