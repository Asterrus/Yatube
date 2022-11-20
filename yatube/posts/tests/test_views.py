import shutil
import tempfile
from collections import namedtuple

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User

# Тесты:
#  При обращении к определённому имени url, вызывается правильный шаблон.
#  В шаблоны передается правильный контекст.

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_USER_COUNT = 2
TEST_GROUP_COUNT = 2


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostsViews(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        test_users = [
            User(username='tester' + str(i)) for i in range(
                1, TEST_USER_COUNT + 1)
        ]
        User.objects.bulk_create(test_users)
        cls.tester_1, cls.tester_2 = User.objects.all()
        # Неавторизованный клиент
        cls.guest_client = Client()
        # Авторизованный клиент
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.tester_1)
        # Авторизованный клиент для проверки подписки
        cls.follower = Client()
        cls.follower.force_login(cls.tester_2)
        # Создание тестовых групп
        test_groups = [Group(
            title='test_group' + str(i),
            slug='test_slug' + str(i),
            description='test_description' + str(i),
        ) for i in range(1, TEST_GROUP_COUNT + 1)]
        Group.objects.bulk_create(test_groups, ignore_conflicts=True)
        cls.t_group1, cls.t_group2 = Group.objects.all()

        cls.t_post = Post.objects.create(
            text='test_text1',
            author=cls.tester_1,
            group=cls.t_group1
        )

        cls.t_comment = Comment.objects.create(
            text='test_comment',
            author=cls.tester_1,
            post=cls.t_post
        )
        cls.page_obj = 'page_obj'
        Page = namedtuple('Page', 'name arg template')
        cls.index_page = Page('posts:index', '', 'posts/index.html')
        cls.group_list_page = Page(
            'posts:group_list', [cls.t_group1.slug], 'posts/group_list.html')
        cls.profile_page = Page(
            'posts:profile', [cls.tester_1.username], 'posts/profile.html')
        cls.post_detail_page = Page(
            'posts:post_detail', [cls.t_post.id], 'posts/post_detail.html')
        cls.post_create_page = Page(
            'posts:post_create', '', 'posts/post_create.html')
        cls.post_edit_page = Page(
            'posts:post_edit', [cls.t_post.id], 'posts/post_create.html')
        cls.add_comment_page = Page('posts:add_comment', [cls.t_post.id], None)
        cls.follow_index_page = Page(
            'posts:follow_index', None, 'posts/follow.html')
        cls.profile_follow_page = Page(
            'posts:profile_follow', [cls.tester_1.username], None)
        cls.profile_unfollow_page = Page(
            'posts:profile_unfollow', [cls.tester_1.username], None)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_templates(self):
        """URL адреса приложения posts используют правильный шаблон."""
        list_pages = [self.index_page, self.group_list_page, self.profile_page,
                      self.post_detail_page, self.post_create_page,
                      self.post_edit_page, self.follow_index_page]
        for page in list_pages:
            with self.subTest(page=page):
                response = self.auth_client.get(
                    reverse(page.name, args=page.arg))
                self.assertTemplateUsed(response, page.template)

    def test_pages_have_1_post(self):
        """Проверка количества постов на страницах
           index, group_list, profile."""
        pages = [self.group_list_page, self.profile_page, self.index_page]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(reverse(
                    page.name, args=page.arg))
                self.assertEqual(len(response.context[self.page_obj]), 1)

    def test_index_page_show_correct_context(self):
        """Проверка корректности контекста в шаблоне
           posts/index.html"""
        response = self.auth_client.get(reverse(self.index_page.name))
        first_object = response.context[self.page_obj][0]
        self.assertEqual(first_object.text, self.t_post.text)
        self.assertEqual(first_object.group.title, self.t_post.group.title)
        self.assertEqual(first_object.author, self.t_post.author)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse(
            self.post_detail_page.name, args=self.post_detail_page.arg))
        context_post = response.context['post']
        post = self.t_post
        self.assertEqual(context_post.text, post.text)
        self.assertEqual(context_post.group, post.group)
        self.assertEqual(context_post.author, post.author)
        self.assertEqual(
            context_post.comments.all()[0],
            post.comments.all()[0]
        )

    def test_post_create_initial_value(self):
        """Предустановленнное значение post_create."""
        response = self.guest_client.get(reverse(self.post_create_page.name))
        self.assertIs(response.context, None)

    def test_post_create_show_correct_context(self):
        """Шаблон create_post создания поста
           сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse(self.post_create_page.name))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон edit_post изменения поста
           сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse(
            self.post_edit_page.name, args=self.post_edit_page.arg))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_with_group_in_all_required_pages(self):
        """Проверка нахождения поста на страницах
           index, group_list и profile."""
        pages = [self.group_list_page, self.profile_page, self.index_page]
        for page in pages:
            with self.subTest(page_name=page):
                response = self.auth_client.get(reverse(
                    page.name, args=page.arg))
                self.assertIn(
                    self.t_post,
                    response.context[self.page_obj].object_list
                )

    def test_post_not_in_wrong_group_list(self):
        """Проверка отсутствия поста группы 2 в списке группы 1."""
        t_post2 = Post.objects.create(
            text='test_text2', author=self.tester_2, group=self.t_group2)
        response = self.guest_client.get(reverse(
            self.group_list_page.name, args=self.group_list_page.arg))

        if response.context[self.page_obj]:
            self.assertNotIn(
                t_post2,
                response.context[self.page_obj].object_list
            )

    def test_post_with_image_correct_context(self):
        """Проверка, что при выводе поста с картинкой
           изображение передаётся в словаре context для
           страниц: index, group_list, post_detail, profile."""
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_image = SimpleUploadedFile(
            name='test.gif',
            content=test_gif,
            content_type='image/gif'
        )
        post_with_image = Post.objects.create(
            text='тестовый пост с ихображением',
            group=self.t_group1,
            author=self.tester_1,
            image=uploaded_image
        )
        # index, group_list, profile
        pages = [self.group_list_page, self.profile_page, self.index_page]
        for page in pages:
            with self.subTest(page=page):
                response = self.auth_client.get(reverse(
                    page.name, args=page.arg))
                # Пост есть на странице
                self.assertIn(
                    post_with_image,
                    response.context[self.page_obj].object_list,
                    'Требуемый пост с картинкой не найден на странице'
                )
                # У поста есть картинка
                self.assertTrue(post_with_image.image)
        # post_detail
        args = [post_with_image.id]
        response = self.auth_client.get(reverse(
            self.post_detail_page.name, args=args))
        self.assertTrue(response.context['post'].image)

    def test_auth_user_can_following(self):
        """Проверка что авторизованный пользователь может подписываться
           на других пользователей и удалять их из подписок"""
        self.follower.get(reverse(
            self.profile_follow_page.name,
            args=self.profile_follow_page.arg))
        self.assertTrue(self.tester_2.follower.filter(
                        author=self.tester_1).exists())

        self.assertRaisesMessage(
            IntegrityError,
            Follow.objects.create(user=self.tester_1, author=self.tester_2))

        self.follower.get(reverse(
            self.profile_unfollow_page.name,
            args=self.profile_unfollow_page.arg))
        self.assertFalse(self.tester_2.follower.filter(
                         author=self.tester_1).exists())

    def test_follower_see_author_post(self):
        """Новая запись пользователя появляется в ленте тех,
           кто на него подписан и не появляется в ленте тех,
           кто не подписан. """

        self.follower.get(reverse(
            self.profile_follow_page.name,
            args=self.profile_follow_page.arg))

        response = self.follower.get(reverse(self.follow_index_page.name))

        self.assertEqual(response.context['posts'][0], self.t_post,
                         'У подписчика не отобразился пост')

        Post(text='тестовый пост', author=self.tester_2).save()
        follower_post = Post.objects.get(text='тестовый пост')

        response = self.follower.get(reverse(self.follow_index_page.name))

        self.assertNotIn(follower_post, response.context['posts'],
                         'Пост отобразился у не подписанного пользователя')
