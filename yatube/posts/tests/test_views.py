
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS_ON_PAGE
from django.core.paginator import Paginator


from ..models import Group, Post, User


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.non_author = User.objects.create_user(username='non_author')
        cls.group = Group.objects.create(
            title='Тест группа',
            slug='test_slug',
            description='Описание',
        )
        cls.scnd_group = Group.objects.create(
            title='Вторая тест группа',
            slug='scnd_test_slug',
            description='Описание второй',
        )

        post_obj = [Post(
            text='Тестовый текст',
            group=cls.group,
            author=cls.author,
            pk='%s' % i
        ) for i in range(12)]
        cls.posts = Post.objects.bulk_create(post_obj)

        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.paginator = Paginator(Post.objects.all(), POSTS_ON_PAGE)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_non_author = Client()
        self.authorized_non_author.force_login(self.non_author)

    def test_pages_uses_correct_template_authorized(self):
        """Использование автором posts view ожидаемых шаблонов."""
        template_pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': '1'}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': 'TestUser'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_correct_template_non_author(self):
        """Использование ложным автором posts view ожидаемых шаблонов."""
        template_pages = {'posts/create_post.html':
                          reverse('posts:post_edit', kwargs={'post_id': '1'}),
                          }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_non_author.get(reverse_name)
                self.assertTemplateNotUsed(response, template)

    def test_create_show_correct_context(self):
        """Проверка форм страницы создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """Проверка форм страницы редактирования поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'}))
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def first_object(self, response):
        """Первый объект из контекста posts views."""
        return response.context['page_obj'][0]

    def test_index_show_correct_context(self):
        """Проверка контекста главной страницы."""
        response = self.guest_client.get(reverse('posts:index'))
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.author: self.first_object(response).author,
            self.post.group: self.first_object(response).group,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_group_list_show_correct_context(self):
        """Проверка контекста страницы постов групп."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        group = response.context['group']
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.author: self.first_object(response).author,
            self.post.group: group,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_wrong_group_list_show_correct_context(self):
        """Проверка отсутствия поста на странице чужой группы."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        group = response.context['group']
        self.assertNotEqual(group, self.scnd_group)

    def test_profile_list_show_correct_context(self):
        """Проверка контекста страницы постов автора."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        author = response.context['author']
        context_counter = response.context['count']
        page_obj = {
            self.post.text: self.first_object(response).text,
            self.post.group: self.first_object(response).group,
            self.post.author: author,
            Post.objects.filter(author=self.author).count(): context_counter,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_detail_show_correct_context(self):
        """Проверка контекста страницы поста."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post_obj = response.context['post']
        author = response.context['author']
        context_counter = response.context['post_count']
        page_obj = {
            self.post.text: post_obj.text,
            self.post.author: author,
            Post.objects.filter(author=self.author).count(): context_counter,
        }
        for obj, context in page_obj.items():
            with self.subTest(context=context):
                self.assertEqual(obj, context)

    def test_first_page_contains_ten_records(self):
        """Первая страница пагинатора -- 10 постов."""
        url_list = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': 'TestUser'}),
        }
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertCountEqual(
                    response.context['page_obj'], POSTS_ON_PAGE)

    def test_first_page_contains_ten_records(self):
        """Вторая страница пагинатора оставшиеся посты."""
        url_list = {
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list', kwargs={
                    'slug': 'test_slug'}) + '?page=2',
            reverse('posts:profile', kwargs={
                    'username': 'TestUser'}) + '?page=2',
        }
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.paginator.count % POSTS_ON_PAGE)
