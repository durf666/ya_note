from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify
from notes.models import Note
from notes.forms import WARNING



class TestNoteCreation(TestCase):
    SLUG = '1'

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(username='testuser')
        cls.user2 = get_user_model().objects.create(username='testuser2')
        cls.note = Note.objects.create(title='Test note', text='Test text', slug=cls.SLUG, author=cls.user)

    def test_anonimous_user_cant_create_note(self):
        client = Client()
        response = client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 302)

    def test_user_can_create_note(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:add'))
        self.assertEqual(response.status_code, 200)

    def test_cant_create_note_with_same_slug(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('notes:add'), {'title': 'Test note', 'text': 'Test text', 'slug': self.SLUG})
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG+WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_note_slug_empty_auto_generated(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('notes:add'), {'title': 'Test note', 'text': 'Test text'})
        self.assertEqual(response.status_code, 302)  # Check for redirect after successful creation
        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.slug, slugify(new_note.title)[:100])
#ToDO вынести в отдельный класс

class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'
    NOTE_TITLE = 'Заголовок заметки'
    NEW_TITLE = 'Новый заголовок'

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(username='testuser')
        cls.user2 = get_user_model().objects.create(username='testuser2')
        cls.note = Note.objects.create(title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, slug='2', author=cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.user2)
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_NOTE_TEXT,
        }

    def test_user_cant_delete_another_user_note(self):
        response = self.reader_client.get(reverse('notes:delete', args=[self.note.slug]))
        self.assertEqual(response.status_code, 404)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_delete_note(self):
        response = self.author_client.post(reverse('notes:delete', args=[self.note.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cant_edit_another_user_note(self):
        response = self.reader_client.get(reverse('notes:edit', args=[self.note.slug]), data=self.form_data)
        self.assertEqual(response.status_code, 404)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


    def test_user_can_edit_note(self):
        response = self.author_client.post(reverse('notes:edit', args=[self.note.slug]), data=self.form_data)
        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NEW_TITLE)
