from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='slug',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_have_correct_object_name(self):
        """Проверка корректной работа __str__ Post."""
        task_post = PostModelTest.post
        self.assertEqual(str(task_post), task_post.text)
        
    def test_post_have_correct_object_name(self):
        """Проверка корректной работа __str__ Group."""                
        task_group = PostModelTest.group
        self.assertEqual(str(task_group), task_group.title)



    def test_group_have_verbose_names(self):
        """проверка имён полей модели Group."""
        task_group = PostModelTest.group
        verboses_group = {
            'title': 'Название группы',
            'slug': 'Ссылка группы',
            'description': 'Описание группы'
        }
        for field, expected_value in verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(task_group._meta.get_field(
                    field).verbose_name, expected_value)
                
    def test_post_have_verbose_names(self):
        """проверка имён полей модели Post."""
        task_post = PostModelTest.post
        verboses_post = {
            'author': 'Автор',
            'text': 'Текст поста',
        }
        for field, expected_value in verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(task_post._meta.get_field(
                    field).verbose_name, expected_value)

    def test_group_have_correct_help_text(self):
        """Проверка наличия описания полей модели Group."""
        task_group = PostModelTest.group
        group_help_texts = {
            'title': 'Введите название группы',
            'slug': ('Укажите адрес. Только '
                     'латиница, цифры, дефисы и знаки подчёркивания'),
            'description': 'Введите описание группы',
        }
        for field, expected_value in group_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(task_group._meta.get_field(
                    field).help_text, expected_value)
    
    def test_post_have_correct_help_text(self):
        """Проверка наличия описания полей модели Post."""
        task_post = PostModelTest.post
        post_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in post_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(task_post._meta.get_field(
                    field).help_text, expected_value)
