from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

class TestNotesList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        Note.objects.create(title='Test note', text='Test text', author=cls.user)

    def test_notes_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertContains(response, 'Test note')

class DifferentUserNotesList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='testuser')
        cls.user2 = User.objects.create(username='testuser2')
        notes = [Note(title=f'Test note {i}', text=f'Test text {i}', slug=f'{i}',
                                     author=cls.user1 if i % 2 == 0 else cls.user2) for i in range(8)]
        Note.objects.bulk_create(notes)

    def testNOtesUserVisibility(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        contains_list = ['Test note 0', 'Test note 2', 'Test note 4', 'Test note 6']
        not_contains_list = ['Test note 1', 'Test note 3', 'Test note 5', 'Test note 7']

        for item in contains_list:
            self.assertContains(response, item)

        for item in not_contains_list:
            self.assertNotContains(response, item)

class TestEditAndCreatePageForms(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.note = Note.objects.create(title='Test title', text='Test text', slug='1', author=cls.user)
        cls.edit_url = reverse('notes:edit', args=[cls.note.slug])
        cls.create_url = reverse('notes:add')



    def test_create_page_has_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.create_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
    def test_edit_page_has_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
