from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

class TestNotesList(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = User.objects.create(username='testuser')
        self.client.force_login(self.user)

    # def test_note_list(self):
    #     url = reverse('notes:list')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)

