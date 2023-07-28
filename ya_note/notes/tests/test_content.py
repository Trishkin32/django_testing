from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from django.test import Client

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            author=cls.author,
        )

    def test_notes_list(self):
        """
        Проверить страницу отдельной заметки,
        что передаётся на страницу со списком заметок
        """
        users_notes = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        url = reverse('notes:list')
        for user, value in users_notes:
            with self.subTest(user=user, value=value):
                response = user.get(url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, value)

    def test_authorized_client_has_form(self):
        """Проверить наличие формы у авторизированного пользовтаеля"""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, value in urls:
            with self.subTest(page):
                url = reverse(page, args=value)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
