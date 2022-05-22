from django.test import Client, TestCase
from posts.models import User


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_pages_all_users(self):
        """Страницы about доступные всем пользователям
        """
        url_list = {
            '/about/author/': 'Страница создателя',
            '/about/tech/': 'Страница стека',
        }
        for url, url_names in url_list.items():
            with self.subTest(url_names=url_names):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_urls_uses_correct_templates(self):
        """Страницы about используют ожидаемые шаблоны
        """
        template_urls = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, url in template_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
