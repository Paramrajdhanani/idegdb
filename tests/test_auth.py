from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.profile_url = '/api/auth/me/'
        self.preferences_url = '/api/auth/preferences/'

    def test_register_user_success(self):
        payload = {
            'username': 'testdev',
            'email': 'testdev@codeforge.dev',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'testdev')
        self.assertTrue(User.objects.filter(username='testdev').exists())

    def test_register_password_mismatch(self):
        payload = {
            'username': 'testdev2',
            'email': 'testdev2@codeforge.dev',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword!'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(username='loginuser', email='login@codeforge.dev', password='SecretPassword123')
        payload = {'username': 'loginuser', 'password': 'SecretPassword123'}
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_preferences_update(self):
        user = User.objects.create_user(username='prefuser', email='pref@codeforge.dev', password='Password123')
        self.client.force_authenticate(user=user)

        update_payload = {
            'theme': 'midnight',
            'font_size': 16,
            'tab_size': 2,
            'word_wrap': False
        }
        response = self.client.put(self.preferences_url, update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'midnight')
        self.assertEqual(response.data['font_size'], 16)
        self.assertEqual(response.data['tab_size'], 2)
