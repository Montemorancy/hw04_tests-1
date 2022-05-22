from itertools import islice

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.posts = (Post(group=cls.group, author=cls.author,
                          text='Тестовый текст', pk='%s' % i)
                     for i in range(15))
        while True:
            batch = list(islice(cls.posts, 15))
            if not batch:
                break
            Post.objects.bulk_create(batch, 15)

        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_non_author = Client()
        self.authorized_non_author.force_login(self.non_author)

    def test_posts_pages_uses_correct_template_all_users(self):
        """Проверка использования posts view 
        ожидаемых шаблонов неавторизованным пользователем
        """
        template_pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': 
                reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
            'posts/post_detail.html': 
                reverse('posts:post_detail', kwargs={'post_id': '1'}),
            'posts/profile.html': 
                reverse('posts:profile', kwargs={'username': 'TestUser'}),
                }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_create_post_correct_template_authorized(self):
        """Проверка использования posts view ожидаемых 
        шаблонов авторизованным пользователем
        """
        template_pages = {
            'posts/create_post.html': reverse('posts:post_create'),
            }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                
    def test_posts_create_post_correct_template_authorized(self):
        """Проверка использования posts view ожидаемых 
        шаблонов автором
        """
        template_pages = {'posts/create_post.html': 
                reverse('posts:post_edit', kwargs={'post_id': '1'}),
                }
        for template, reverse_name in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_non_author.get(reverse_name)
                self.assertTemplateNotUsed(response, template)

    def test_create_show_correct_context(self):
        """Проверка контекста страницы создания поста"""
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
        """Проверка контекста страницы редактирования поста"""
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

    def test_index_show_correct_context(self):
        """Проверка контекста главной страницы"""
        response = self.guest_client.get(reverse('posts:index'))
        first_obj = response.context['page_obj'][0]
        text_0 = first_obj.text
        author_0 = first_obj.author
        group_0 = first_obj.group
        self.assertEqual(text_0, self.post.text)
        self.assertEqual(group_0, self.post.group)
        self.assertEqual(author_0, self.post.author)

    def test_group_list_show_correct_context(self):
        """Проверка контекста страницы постов групп"""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        first_obj = response.context['page_obj'][0]
        text_0 = first_obj.text
        author_0 = first_obj.author
        group_0 = first_obj.group
        self.assertEqual(text_0, self.post.text)
        self.assertEqual(group_0, self.post.group)
        self.assertEqual(author_0, self.post.author)
        self.assertNotEqual(group_0, self.scnd_group)

    def test_profile_list_show_correct_context(self):
        """Проверка контекста страницы постов автора"""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'TestUser'}))
        first_obj = response.context['page_obj'][0]
        text_0 = first_obj.text
        author_0 = first_obj.author
        self.assertEqual(text_0, self.post.text)
        self.assertEqual(author_0, self.post.author)

    def test_detail_show_correct_context(self):
        """Проверка контекста страницы поста"""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
            )
        obj = response.context['post'].text
        self.assertEqual(obj, self.post.text)

    def test_first_page_contains_ten_records(self):
        """Проверка работы первой страницы паджинатора главной страницы"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_first_page_contains_ten_records(self):
        """Проверка работы первой страницы паджинатора постов группы"""        
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_first_page_contains_ten_records(self):
        """Проверка работы первой страницы паджинатора постов автора"""        
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'TestUser'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка работы второй страницы паджинатора главной страницы"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_second_page_contains_three_records(self):
        """Проверка работы второй страницы паджинатора постов группы"""
        response = self.client.get(reverse('posts:group_list', kwargs={
                                   'slug': 'test_slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_second_page_contains_three_records(self):
        """Проверка работы второй страницы паджинатора постов автора"""
        response = self.client.get(reverse('posts:profile', kwargs={
                                   'username': 'TestUser'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 6)
