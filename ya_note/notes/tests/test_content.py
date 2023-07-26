from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            author=cls.author,
        )

    def test_notes_list(self):
        """
        Проверить страницу отдельной заметки,
        что передаётся на страницу со списком заметок
        """
        users_notes = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, value in users_notes:
            self.client.force_login(user)
            with self.subTest(user=user, value=value):
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, value)

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, value in urls:
            with self.subTest(page):
                self.client.force_login(self.author)
                url = reverse(page, args=value)
                response = self.client.get(url)
                self.assertIn('form', response.context)
