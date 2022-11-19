from django.test import TestCase

from ..models import POST_STR_NAME_LENGTH, Group, Post, User

# Тесты:
#  Валидация полей моделей.
#  Методы по работе с моделями.


class PostModelText(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост длиной больше 15 символов',
            author=cls.user)

    def test_models_have_correct_object_names(self):
        """Проверка корректности работы метода __str__
           у моделей приложения posts."""
        objects_and_expected_names = {
            self.group: self.group.title,
            self.post: self.post.text[:POST_STR_NAME_LENGTH]
        }
        for object, expected_name in objects_and_expected_names.items():
            with self.subTest(object=object):
                self.assertEqual(expected_name, str(object))

    def test_post_models_correct_help_texts(self):
        """Проверка корректности вспомогательного текста
           help_text у модели Post приложения posts."""
        fields_help_texts = {
            'text': 'Введите текст',
            'group': 'Выбор группы, к которой относится текст'
        }
        for field, expected_help_text in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_help_text
                )

    def test_post_model_verbose_name(self):
        """Проверка корректности vetbose_name
           у модели Post приложения posts."""
        fields_verbose_names = {
            'text': 'Текст',
            'created': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_verbose_name in fields_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_verbose_name
                )
