from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import User


class UsersCreateUserTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tester = Client()
        tester = User.objects.create(username='tester')
        cls.tester.force_login(tester)

    def test_create_user(self):
        """Валидная форма создает пользователя в User."""
        users_count = User.objects.count()
        form_data = {
            'username': 'tester2',
            'password1': 'TestPass1!',
            'password2': 'TestPass1!'
        }
        response = self.tester.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='tester2',
            ).exists()
        )

    def test_cant_create_existing_user(self):
        """Проверка невозможности создания пользователя,
           если пользователь с таким username уже существует"""
        users_count = User.objects.count()
        form_data = {
            'username': 'tester',
            'password1': 'TestPass1!',
            'password2': 'TestPass1!'
        }
        response = self.tester.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count)
        self.assertFormError(
            response,
            'form',
            'username',
            'Пользователь с таким именем уже существует.'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
