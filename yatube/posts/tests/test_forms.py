from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm

from ..models import Group, Post, User


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тест группа',
            slug='test_slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_create_post_forms(self):
        """Проверка формы создания поста."""
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'slug': self.group.slug,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=(self.post.author, )))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            author=self.post.author,
            text=self.post.text,
            group=self.post.group,
        ).exists())

    def test_post_edit_form_show_correct_context(self):
        """Шаблон post edit сформирован с правильным контекстом."""
        response = self.authorized_user.get(
            reverse('posts:post_edit', args={self.post.pk, }))
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['is_edit'], True)
