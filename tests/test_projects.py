from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from languages.models import Language
from projects.models import Project, ProjectFile

class ProjectAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='projdev', email='proj@codeforge.dev', password='Password123')
        self.client.force_authenticate(user=self.user)

        self.language = Language.objects.create(
            name='Python',
            slug='python',
            version='3.13',
            monaco_id='python',
            file_extension='.py',
            default_filename='main.py',
            default_code='print("hello world")',
            run_command='python {entry_file}',
            is_active=True
        )

    def test_create_project_auto_creates_entry_file(self):
        payload = {
            'name': 'My Python Project',
            'language_slug': 'python',
            'description': 'Testing auto file creation'
        }
        response = self.client.post('/api/projects/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project_id = response.data['id']
        project = Project.objects.get(id=project_id)
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.files.count(), 1)
        entry_file = project.files.first()
        self.assertEqual(entry_file.name, 'main.py')
        self.assertTrue(entry_file.is_entry_point)

    def test_project_file_crud(self):
        project = Project.objects.create(
            owner=self.user,
            name='Multi-File Test',
            language=self.language
        )

        # Create secondary helper file
        file_payload = {
            'name': 'helper.py',
            'path': 'utils',
            'content': 'def add(a, b): return a + b',
            'is_entry_point': False
        }
        res = self.client.post(f'/api/projects/{project.id}/files/', file_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        file_id = res.data['id']

        # Update file content
        update_payload = {'content': 'def add(a, b): return a + b + 1'}
        patch_res = self.client.patch(f'/api/files/{file_id}/', update_payload, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['content'], 'def add(a, b): return a + b + 1')

    def test_duplicate_project(self):
        project = Project.objects.create(
            owner=self.user,
            name='Original App',
            language=self.language
        )
        ProjectFile.objects.create(
            project=project,
            name='main.py',
            content='print("original")',
            is_entry_point=True
        )

        res = self.client.post(f'/api/projects/{project.id}/duplicate/')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('(Copy)', res.data['name'])
        dup_id = res.data['id']
        dup_project = Project.objects.get(id=dup_id)
        self.assertEqual(dup_project.files.count(), 1)

    def test_download_project_zip(self):
        project = Project.objects.create(
            owner=self.user,
            name='Zip Export App',
            language=self.language
        )
        ProjectFile.objects.create(
            project=project,
            name='main.py',
            content='print("zip test")',
            is_entry_point=True
        )

        res = self.client.get(f'/api/projects/{project.id}/download/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/zip')
