from http import HTTPStatus as HTTPs

from django.test import Client, TestCase
from posts.models import User

from ..models import Group, Post

# Тесты:
#  Страницы доступны по ожидаемому адресу.
#  Для страниц вызывается ожидаемый HTML-шаблон.
#  При отсутствии доступа к страницы происходит переадрисация.


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Неавторизованный клиент
        cls.guest_client = Client()
        # Авторизованный клиент
        cls.tester = Client()
        cls.usr = User.objects.create(username='tester')
        cls.tester.force_login(cls.usr)
        # Авторизованный клиент(не автор поста)
        cls.no_author = Client()
        cls.user_no_author = User.objects.create(username='no_author')
        cls.no_author.force_login(cls.user_no_author)

        group1 = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Это группа, созданная для тестов'
        )
        post1 = Post.objects.create(
            text='Тестовый текст',
            author=cls.usr,
            group=group1
        )

        cls.urls_and_templates_auth_required = {
            'create': ('/create/', 'posts/post_create.html'),
            'post_edit': (
                f'/posts/{post1.id}/edit/', 'posts/post_create.html'),
            'add_comment': (f'/posts/{post1.id}/comment/', None),
            'follow_index': ('/follow/', 'posts/follow.html'),
            'profile_follow': (f'/profile/{cls.usr.username}/follow/', None),
            'profile_unfollow': (
                f'/profile/{cls.usr.username}/unfollow/', None),
        }

        cls.urls_and_templates_no_auth = {
            'index': ('/', 'posts/index.html'),
            'group_list': (f'/group/{group1.slug}/', 'posts/group_list.html'),
            'profile': (f'/profile/{cls.usr.username}/', 'posts/profile.html'),
            'post_detail': (f'/posts/{post1.id}/', 'posts/post_detail.html')
        }

        cls.error_pages = {
            '404': ('/unexisting_page/', 'core/404.html', HTTPs.NOT_FOUND),
            '403': (None, 'core/403csrf.html', HTTPs.FORBIDDEN)
        }

    def test_urls_exists_at_desired_locations_for_guest_user(self):
        """Проверка доступности адресов для
           неавторизованного пользователя."""
        for name in self.urls_and_templates_no_auth:
            url = self.urls_and_templates_no_auth[name][0]
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPs.OK.value)

    def test_errors_page_status_code_templates(self):
        """Проверка вывода правильного шаблона
           для страниц ошибок"""
        for url, template, status in self.error_pages.values():
            with self.subTest(url=url):
                if url:
                    response = self.tester.get(url)
                    self.assertEqual(response.status_code, status.value)
                    self.assertTemplateUsed(response, template)

    def test_post_create_url_redirect_guest_user_to_login_page(self):
        """Проверка перенаправления неавторизованного пользователя
           на страницу авторизации для страниц требующих авторизации."""
        for name in self.urls_and_templates_auth_required:
            with self.subTest(name=name):
                url = self.urls_and_templates_auth_required[name][0]
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response,
                    '/auth/login/?next=' + url)

    def test_post_create_url_access_for_authorised_user(self):
        """Проверка доступности для авторизованного пользователя
           страницы создания поста."""
        create_name = self.urls_and_templates_auth_required['create'][0]
        response = self.tester.get(create_name)
        self.assertEqual(response.status_code, HTTPs.OK.value)

    def test_add_comment_redirect_for_authorised_user(self):
        """Проверка перенаправления авторизованного пользователя
           на страницу описания поста, при переходе
           по ссылке post/add_comment """
        add_comment = self.urls_and_templates_auth_required['add_comment'][0]
        det_name = self.urls_and_templates_no_auth['post_detail'][0]
        response = self.tester.get(add_comment)
        self.assertRedirects(response, det_name)

    def test_post_edit_url_redirect_if_not_author(self):
        """Проверка перенаправления пользователя со страницы
           изменения поста, если пользователь не автор этого поста."""
        edit_name = self.urls_and_templates_auth_required['post_edit'][0]
        det_name = self.urls_and_templates_no_auth['post_detail'][0]
        response = self.no_author.get(edit_name, follow=True)
        self.assertRedirects(response, det_name)

    def test_post_edit_url_access_for_author(self):
        """Проверка доступности страницы изменения поста, для автора поста."""
        edit_name = self.urls_and_templates_auth_required['post_edit'][0]
        response = self.tester.get(edit_name)
        self.assertEqual(response.status_code, HTTPs.OK.value)

    def test_posts_urls_uses_correct_templates(self):
        """Проверка использования правильных шаблонов
           url адресами в приложении posts."""
        all_posts_urls_and_templates = dict(
            ** self.urls_and_templates_auth_required,
            ** self.urls_and_templates_no_auth)
        for url, template in all_posts_urls_and_templates.values():
            if template:
                with self.subTest(url=url):
                    response = self.tester.get(url)
                    self.assertTemplateUsed(response, template)
