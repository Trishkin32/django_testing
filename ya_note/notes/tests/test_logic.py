from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    ADD_URL = reverse('notes:add')
    TITLE = 'Новый заголовок'
    TEXT = 'Новый текст'
    SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'author': 'Автор',
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'slug',
        }

    def test_user_can_create_note(self):
        """
        Проверить, что залогиненный пользователь
        может оставить заметку
        """
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        notes = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(notes.title, self.form_data['title'])
        self.assertEqual(notes.text, self.form_data['text'])
        self.assertEqual(notes.slug, self.form_data['slug'])
        self.assertEqual(notes.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """
        Проверить, что анонимный пользователь
        не может оставить заметку
        """
        self.client.post(self.ADD_URL, data=self.form_data)
        notes_in_db = Note.objects.count()
        self.assertEqual(notes_in_db, 0)

    def test_new_slug_not_old_slug(self):
        """Проверить что нельзя создать две заметки с одинаковым slug"""
        self.auth_client.post(self.ADD_URL, data=self.form_data)
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(response, form='form',
                             field='slug', errors=warning)

    def test_auto_slug(self):
        """Проверить автоматическое создание слага"""
        self.form_data.pop('slug')
        response = self.auth_client.post(self.ADD_URL, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        slugify_slug = slugify(self.form_data['title'])
        note_slug = Note.objects.get(slug=slugify_slug)
        self.assertEqual(slugify_slug, note_slug.slug)


class TestNoteEditDelete(TestCase):
    NEW_TITLE = 'Новый заголовок'
    NEW_TEXT = 'Новый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
        }

    def test_author_can_edit_note(self):
        """Проверить что автор может редактировать свои заметки"""
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_author_can_delete_note(self):
        """Проверить, что автор может удалить свою заметки"""
        response = self.author_client.post(self.delete_url,
                                           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_in_db_count = Note.objects.count()
        self.assertEqual(notes_in_db_count, 0)

    def test_user_can_edit_note(self):
        """Проверить что пользователь не может редактировать чужие заметки"""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        note_db = Note.objects.get(slug=self.note.slug)
        self.assertEqual(self.note.title, note_db.title)
        self.assertEqual(self.note.text, note_db.text)

    def test_user_can_delete_note(self):
        """Проверить что пользователь не может удалять чужие заметки"""
        response = self.reader_client.post(self.delete_url,
                                           data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
