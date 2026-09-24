from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from languages.models import Language

class LanguagesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        Language.objects.create(
            name='Python',
            slug='python',
            version='3.13',
            monaco_id='python',
            file_extension='.py',
            default_filename='main.py',
            default_code='print("python")',
            run_command='python {entry_file}',
            is_active=True
        )
        Language.objects.create(
            name='Inactive Lang',
            slug='inactive',
            version='1.0',
            run_command='bin',
            is_active=False
        )

    def test_list_active_languages_only(self):
        res = self.client.get('/api/languages/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        slugs = [l['slug'] for l in res.data]
        self.assertIn('python', slugs)
        self.assertNotIn('inactive', slugs)

    def test_get_language_detail(self):
        res = self.client.get('/api/languages/python/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'Python')
        self.assertEqual(res.data['monaco_id'], 'python')
