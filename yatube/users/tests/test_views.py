from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User

names_templates = {
    'users:logout': 'users/logged_out.html',
    'users:login': 'users/login.html',
    'users:password_reset': 'users/password_reset_form.html',
    'users:password_reset_done': 'users/password_reset_done.html',
    'users:reset_done': 'users/password_reset_complete.html',
    'users:signup': 'users/signup.html'
}


class TestUsersViews(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.guest_client = Client()
        cls.auth_client = Client()
        cls.tester = User.objects.create(username='tester')
        cls.auth_client.force_login(cls.tester)

    def test_login_view_uses_correct_template(self):
        """URL адрес использует правильный шаблон."""
        for name, template in names_templates.items():
            with self.subTest(name=name):
                response = self.auth_client.get(reverse(name))
                self.assertTemplateUsed(response, template)

    def test_signup_uses_correct_form(self):
        """Проверка корректности формы переданной в signup."""
        url_signup = list(names_templates.keys())[5]
        response = self.auth_client.get(reverse(url_signup))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.CharField,
            'password2': forms.CharField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
