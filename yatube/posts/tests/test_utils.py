from core.views import POSTS_ON_PAGE
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Создание клиента и постов для проверки пагинатора."""
        super().setUpClass()
        cls.guest_client = Client()
        cls.paginator_tester = User.objects.create(username='paginator_tester')
        post_test_objects = [Post(
            text=str(i),
            author=cls.paginator_tester
        ) for i in range(POSTS_ON_PAGE + 1)]
        Post.objects.bulk_create(post_test_objects)

        cls.page_obj = 'page_obj'
        cls.index_page = 'posts:index'
        cls.post_test = Post.objects.get(id=1)

    def test_first_page_contains_required_records(self):
        """Проверка количества постов на первой странице."""
        response = self.guest_client.get(reverse(self.index_page))
        self.assertEqual(len(response.context[self.page_obj]), POSTS_ON_PAGE)

    def test_second_page_contains_required_records(self):
        """Проверка количества постов на второй странице."""
        response = self.guest_client.get(reverse(self.index_page) + '?page=2')
        self.assertEqual(len(response.context[self.page_obj]), 1)

    def test_cache_test(self) -> None:
        'Работа кэша'
        response_1 = self.guest_client.get(reverse(self.index_page))
        Post.objects.create(text='test_post', author=self.paginator_tester)
        response_2 = self.guest_client.get(reverse(self.index_page))
        self.assertEqual(
            response_1.content,
            response_2.content,
            'Результат запросов до создания поста и после создания отличается')
        cache.clear()
        response_3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(
            response_1.content,
            response_3.content,
            'Результат запроса после очистки кэша не изменился')
