from django.test import Client, TestCase
from http import HTTPStatus

from ..models import Group, Post, User


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Описание тестовой группы',
        )
        cls.main_user = User.objects.create(username='TestUser')
        cls.scnd_user = User.objects.create(username='ScndTestUser')
        cls.post = Post.objects.create(
            author=cls.main_user,
            text='Тестовый текст',
        )
        cls.scnd_user_post = Post.objects.create(
            author=cls.scnd_user,
            text='Тестовый текст второго пользователя'
        )

    def setUp(self):
        self.guest_client = Client()
        self.main_client = Client()
        self.main_client.force_login(self.main_user)
        self.scnd_client = Client()
        self.scnd_client.force_login(self.scnd_user)

    def test_pages_unuthorized_users(self):
        """Страницы posts доступные неавторизованным пользователям."""
        url_list = {
            '/': 'Главная страница',
            '/group/test-slug/': 'Страница групп',
            '/profile/TestUser/': 'Посты пользователя',
            '/posts/1/': 'Страница поста',
        }
        for url, url_names in url_list.items():
            with self.subTest(url_names=url_names):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect_unuthorized_users(self):
        """Страницы posts не доступные неавторизованным пользователям."""
        url_list = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/posts/1/',
        }
        for url, url_names in url_list.items():
            with self.subTest(url_names=url_names):
                response = self.guest_client.get(url)
                self.assertRedirects(response, url_names)
                # Несуществующая страница
                response = self.guest_client.get('/unexpected-page/')
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_author(self):
        """Страницы posts доступные автору."""
        url_list = {
            '/': 'Главная страница',
            '/group/test-slug/': 'Страница групп',
            '/profile/TestUser/': 'Посты пользователя',
            '/posts/1/': 'Страница поста',
            '/create/': 'Создание поста',
            '/posts/1/edit/': 'Редактирования поста',
        }
        for url, url_names in url_list.items():
            with self.subTest(url_names=url_names):
                response = self.main_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirects_non_author(self):
        """Страницы posts не доступные автору."""
        # Страница редактирования чужого поста
        response = self.main_client.get('/posts/2/edit/')
        self.assertRedirects(response, '/posts/2/')
        # Несуществующая страница
        response = self.main_client.get('/unexpected-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_templates(self):
        """Страницы posts соответствуют шаблонам."""
        templates_urls = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/create/',
            'posts/profile.html': '/profile/TestUser/',
        }
        for template, url in templates_urls.items():
            with self.subTest(url=url):
                response = self.main_client.get(url)
                self.assertTemplateUsed(response, template)
