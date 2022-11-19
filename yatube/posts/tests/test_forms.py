import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

# Тесты:
# После успешной валидации в моделях появляются новые записи.
# После отправки валидной формы происходит корректная переадресация.

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


test_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

uploaded_image_1 = SimpleUploadedFile(
    name='test.gif',
    content=test_gif,
    content_type='image/gif'
)

uploaded_image_2 = SimpleUploadedFile(
    name='test2.gif',
    content=test_gif,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Неавторизованный клиент
        cls.guest_user = Client()
        # Авторизованный клиент
        cls.tester = Client()
        cls.usr = User.objects.create(username='tester')
        cls.tester.force_login(cls.usr)
        # Авторизованный клиент(не автор поста)
        cls.no_author = Client()
        cls.user_no_author = User.objects.create(username='no_author')
        cls.no_author.force_login(cls.user_no_author)

        cls.t_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='тестовая группа'
        )

        cls.t_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.usr
        )

        cls.names_with_args = {
            'profile': ('posts:profile', {'username': cls.usr.username}),
            'post_detail': ('posts:post_detail', {'post_id': cls.t_post.id}),
            'post_create': ('posts:post_create', {}),
            'post_edit': ('posts:post_edit', {'post_id': cls.t_post.id}),
            'add_comment': ('posts:add_comment', {'post_id': cls.t_post.id})
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post.
           Происходит перенаправление на страницу профиля."""
        posts_count: int = Post.objects.count()
        new_post_text = 'Текст нового поста'
        create_name = self.names_with_args['post_create'][0]
        prof_name, prof_args = self.names_with_args['profile']
        form_data = {
            'author': self.usr,
            'text': new_post_text,
            'image': uploaded_image_1
        }
        response = self.tester.post(reverse(create_name),
                                    data=form_data, follow=True)

        self.assertRedirects(response, reverse(
            prof_name, kwargs=prof_args))

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            author=self.usr, text=new_post_text,
            image='posts/test.gif').exists())

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post.
           Происходит перенаправление на страницу поста.
           Проверка корректного изменения группы."""
        posts_count: int = Post.objects.count()
        edit_name, edit_args = self.names_with_args['post_edit']
        det_name, det_args = self.names_with_args['post_detail']
        new_text = 'Новый текст'
        form_data = {
            'author': self.usr, 'text': new_text,
            'group': self.t_group.id, 'image': uploaded_image_2
        }
        response = self.tester.post(reverse(edit_name, kwargs=edit_args),
                                    data=form_data, follow=True)

        self.assertRedirects(response, reverse(det_name, kwargs=det_args))
        self.assertEqual(Post.objects.count(), posts_count)

        self.assertTrue(Post.objects.filter(
            author=self.usr, text=new_text,
            group=self.t_group.id, image='posts/test2.gif').exists())

        self.assertIs(Post.objects.filter(
            author=self.usr, text=self.t_post.text).exists(), False)

    def test_no_auth_user_create_post(self):
        """Проверка отсутствия возможности неавторизованному
           пользователю создать пост."""
        posts_count = Post.objects.count()
        create_name = self.names_with_args['post_create'][0]
        form_data = {
            'author': self.usr,
            'text': 'Тестовый текст, пользователь не авторизован',
        }
        response = self.guest_user.post(reverse(create_name),
                                        data=form_data, follow=True)

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response,
            '/auth/login/?next=' + reverse(create_name)
        )

    def test_no_registered_user_edit_post(self):
        """Проверка отсутствия возможности неавторизованному
           пользователю изменять пост и перенаправления
           на страницу авторизации"""
        edit_name, edit_args = self.names_with_args['post_edit']
        text_no_login = 'Тестовый текст, пользователь не авторизован'
        form_data = {'author': self.usr, 'text': text_no_login}

        response = self.guest_user.post(reverse(edit_name, kwargs=edit_args),
                                        data=form_data, follow=True)

        self.assertRedirects(
            response,
            '/auth/login/?next=' + reverse(edit_name, kwargs=edit_args)
        )

        self.assertTrue(Post.objects.filter(
            author=self.usr, text=self.t_post.text).exists())

        self.assertIs(Post.objects.filter(
            author=self.usr, text=text_no_login).exists(), False)

    def test_no_author_user_edit_post(self):
        """Проверка отсутствия возможности пользователю
           не являющемуся автором поста изменять пост и
           перенаправления на страницу описания поста."""
        text_no_author = 'Тестовый текст, пользователь не является автором'
        form_data = {'author': self.usr, 'text': text_no_author}
        edit_name, edit_args = self.names_with_args['post_edit']
        det_name, det_args = self.names_with_args['post_detail']

        response = self.no_author.post(reverse(edit_name, kwargs=edit_args),
                                       data=form_data, follow=True)

        self.assertRedirects(response, reverse(det_name, kwargs=det_args))

        self.assertTrue(Post.objects.filter(
            author=self.usr, text=self.t_post.text).exists())
        self.assertIs(Post.objects.filter(
            author=self.usr, text=text_no_author,).exists(), False)

    def test_add_comment_valid_form(self):
        """Валидная форма создает запись в Comment.
           Происходит перенаправление на страницу поста."""
        comment_count: int = Comment.objects.count()
        comment_text = 'Текст нового комментария'
        add_comment, add_comm_args = self.names_with_args['add_comment']
        det_name, det_args = self.names_with_args['post_detail']
        form_data = {
            'author': self.usr,
            'text': comment_text,
            'post': self.t_post
        }
        response = self.tester.post(reverse(add_comment, kwargs=add_comm_args),
                                    data=form_data, follow=True)
        self.assertRedirects(response, reverse(det_name, kwargs=det_args))

        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            author=self.usr, text=comment_text).exists())

    def test_add_comment_no_login(self):
        """Проверка отсутствия возможности неавторизованному
           пользователю создавать комментарий и перенаправления
           на страницу авторизации"""
        comment_count: int = Comment.objects.count()
        comment_text = 'Комментарий от неавторизованного пользователя'
        add_comment, add_comm_args = self.names_with_args['add_comment']
        form_data = {
            'author': self.usr,
            'text': comment_text,
            'post': self.t_post
        }
        response = self.guest_user.post(
            reverse(add_comment, kwargs=add_comm_args),
            data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=' + reverse(add_comment, kwargs=add_comm_args))

        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertFalse(Comment.objects.filter(
            author=self.usr, text=comment_text).exists())
