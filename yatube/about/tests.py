from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

urls_and_names_templates = {
    '/about/author/': ('about:author', 'about/about_author.html'),
    '/about/tech/': ('about:tech', 'about/about_tech.html')
}


class AboutURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_urls_exists_at_desire_location(self):
        """Проверка доступности url в приложении about по их адресам."""
        for url in urls_and_names_templates:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)


class AboutViewsTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_pages_accesible_by_name(self):
        """Проверка доступности url в приложении about по их именам."""
        for name_template in urls_and_names_templates.values():
            name = name_template[0]
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_author_page_uses_correct_template(self):
        """Проверка использования правильных шаблонов в приложении about."""
        for name_template in urls_and_names_templates.values():
            name, template = name_template
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertTemplateUsed(response, template)
