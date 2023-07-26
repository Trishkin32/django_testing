from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='note-slug',
        )

    def test_pages_availability(self):
        """
        Страницы доступны для всех пользователей:
        главная, регистрации, входа и выхода учетной записи
        """
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for address in urls:
            with self.subTest(address):
                url = reverse(address)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Проверить страницы доступности для авторизованного пользователя"""
        urls = (
            'notes:list',
            'notes:success',
            'notes:add',
        )
        for address in urls:
            with self.subTest(address):
                url = reverse(address)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """
        Проверить страницы отдельной заметки,
        удаления и редактирования заметки
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        urls = (
            'notes:edit',
            'notes:detail',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for address in urls:
                with self.subTest(user=user, address=address):
                    url = reverse(address, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверить перенаправление для неавторизованного пользователя."""
        login_url = reverse('users:login')
        ursl = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for address, value in ursl:
            with self.subTest(address=address):
                url = reverse(address, args=value)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
