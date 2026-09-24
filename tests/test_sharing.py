from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from languages.models import Language
from projects.models import Project, ProjectFile
from sharing.models import ProjectShare

class SharingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='shareowner', email='owner@codeforge.dev', password='Password123')
        self.client.force_authenticate(user=self.user)

        self.language = Language.objects.create(
            name='Python',
            slug='python',
            version='3.13',
            monaco_id='python',
            file_extension='.py',
            default_filename='main.py',
            run_command='python {entry_file}',
            is_active=True
        )

        self.project = Project.objects.create(
            owner=self.user,
            name='Shared Portfolio Project',
            language=self.language
        )
        ProjectFile.objects.create(
            project=self.project,
            name='main.py',
            content='print("Shared Project Content")',
            is_entry_point=True
        )

    def test_generate_share_token(self):
        res = self.client.post(f'/api/projects/{self.project.id}/share/', {'permission': 'read_only'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', res.data)
        self.assertIn('share_url', res.data)
        self.assertIn('embed_code', res.data)

    def test_access_project_via_share_token_unauthenticated(self):
        share = ProjectShare.objects.create(
            project=self.project,
            permission='read_only'
        )

        # Unauthenticated client accesses share endpoint
        anon_client = APIClient()
        res = anon_client.get(f'/api/share/{share.token}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['project']['name'], 'Shared Portfolio Project')
        self.assertEqual(len(res.data['project']['files']), 1)

        # Verify view count increment
        share.refresh_from_db()
        self.assertEqual(share.view_count, 1)
