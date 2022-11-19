import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

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
        cls.names_args_templates = {
            'index': ('posts:index', {}, 'posts/index.html'),
            'group_list': (
                'posts:group_list', {'group_slug': cls.t_group1.slug},
                'posts/group_list.html'),
            'profile': (
                'posts:profile', {'username': cls.tester_1.username},
                'posts/profile.html'),
            'post_detail': (
                'posts:post_detail', {'post_id': cls.t_post.id},
                'posts/post_detail.html'),
            'post_create': ('posts:post_create', {}, 'posts/post_create.html'),
            'post_edit': (
                'posts:post_edit', {'post_id': cls.t_post.id},
                'posts/post_create.html'),
            'add_comment': (
                'posts:add_comment', {'post_id': cls.t_post.id},
                None),
            'follow_index': ('posts:follow_index', {}, 'posts/follow.html'),
            'profile_follow': (
                'posts:profile_follow', {'username': cls.tester_1.username},
                None),
            'profile_unfollow': (
                'posts:profile_unfollow', {'username': cls.tester_1.username},
                None),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_templates(self):
        """URL адреса приложения posts используют правильный шаблон."""
        for name in self.names_args_templates:
            url_name, args, template = self.names_args_templates[name]
            if template:
                with self.subTest(name=name):
                    response = self.auth_client.get(
                        reverse(url_name, kwargs=args))
                    self.assertTemplateUsed(response, template)

    def test_pages_have_1_post(self):
        """Проверка количества постов на страницах
           index, group_list, profile."""
        required_pages = ['index', 'group_list', 'profile']
        for page in required_pages:
            with self.subTest(page=page):
                name, args = self.names_args_templates[page][:2]
                response = self.guest_client.get(reverse(name, kwargs=args))
                self.assertEqual(len(response.context[self.page_obj]), 1)

    def test_index_page_show_correct_context(self):
        """Проверка корректности контекста в шаблоне
           posts/index.html"""
        index_name = self.names_args_templates['index'][0]
        response = self.auth_client.get(reverse(index_name))
        first_object = response.context[self.page_obj][0]
        self.assertEqual(first_object.text, self.t_post.text)
        self.assertEqual(first_object.group.title, self.t_post.group.title)
        self.assertEqual(first_object.author, self.t_post.author)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        det_name, args = self.names_args_templates['post_detail'][:2]
        response = self.auth_client.get(reverse(det_name, kwargs=args))
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
        create_name = self.names_args_templates['post_create'][0]
        response = self.guest_client.get(reverse(create_name))
        self.assertIs(response.context, None)

    def test_post_create_show_correct_context(self):
        """Шаблон create_post создания поста
           сформирован с правильным контекстом."""
        create_name = self.names_args_templates['post_create'][0]
        response = self.auth_client.get(reverse(create_name))
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
        edit_name, args = self.names_args_templates['post_edit'][:2]
        response = self.auth_client.get(reverse(edit_name, kwargs=args))
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
        required_paths = ['index', 'group_list', 'profile']
        for page in required_paths:
            with self.subTest(page_name=page):
                name, args = self.names_args_templates[page][:2]
                response = self.auth_client.get(reverse(name, kwargs=args))
                self.assertIn(
                    self.t_post,
                    response.context[self.page_obj].object_list
                )

    def test_post_not_in_wrong_group_list(self):
        """Проверка отсутствия поста группы 2 в списке группы 1."""
        t_post2 = Post.objects.create(
            text='test_text2', author=self.tester_2, group=self.t_group2)
        group_name, args = self.names_args_templates['group_list'][:2]
        response = self.guest_client.get(reverse(group_name, kwargs=args))

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
        required_paths = ['index', 'group_list', 'profile']
        for page in required_paths:
            with self.subTest(page=page):
                name, args = self.names_args_templates[page][:2]
                response = self.auth_client.get(reverse(name, kwargs=args))
                # Пост есть на странице
                self.assertIn(
                    post_with_image,
                    response.context[self.page_obj].object_list,
                    'Требуемый пост с картинкой не найден на странице'
                )
                # У поста есть картинка
                self.assertTrue(post_with_image.image)
        # post_detail
        det_name = self.names_args_templates['post_detail'][0]
        args = {'post_id': post_with_image.id}
        response = self.auth_client.get(reverse(det_name, kwargs=args))
        self.assertTrue(response.context['post'].image)

    def test_auth_user_can_following(self):
        """Проверка что авторизованный пользователь может подписываться
           на других пользователей и удалять их из подписок"""
        self.follower.get(reverse(
            self.names_args_templates['profile_follow'][0],
            kwargs=self.names_args_templates['profile_follow'][1]))
        self.assertTrue(self.tester_2.follower.filter(
                        author=self.tester_1).exists())
        self.follower.get(reverse(
            self.names_args_templates['profile_unfollow'][0],
            kwargs=self.names_args_templates['profile_unfollow'][1]))
        self.assertFalse(self.tester_2.follower.filter(
                         author=self.tester_1).exists())

    def test_follower_see_author_post(self):
        """Новая запись пользователя появляется в ленте тех,
           кто на него подписан и не появляется в ленте тех,
           кто не подписан. """

        self.follower.get(reverse(
            self.names_args_templates['profile_follow'][0],
            kwargs=self.names_args_templates['profile_follow'][1]))

        response = self.follower.get(reverse(
            self.names_args_templates['follow_index'][0]))

        self.assertEqual(response.context['posts'][0], self.t_post,
                         'У подписчика не отобразился пост')

        Post(text='тестовый пост', author=self.tester_2).save()
        follower_post = Post.objects.get(text='тестовый пост')

        response = self.auth_client.get(reverse(
            self.names_args_templates['follow_index'][0]))

        self.assertNotIn(follower_post, response.context['posts'],
                         'Пост отобразился у не подписанного пользователя')
