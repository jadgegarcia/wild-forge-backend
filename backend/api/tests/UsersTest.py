from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User
from api.serializers import UserSerializer
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

class UsersTest(TestCase):
    def setUp(self):
        # Create a superuser
        self.superuser = User.objects.create(
            email='superuser@example.com',
            password='superuserpassword',
            first_name='Super',
            last_name='User',
            is_superuser=True
        )

        # Create a regular user
        self.regular_user = User.objects.create(
            email='user@example.com',
            password='userpassword',
            first_name='Regular',
            last_name='User',
        )

        # Create JWT tokens for authentication
        superuser_refresh = RefreshToken.for_user(self.superuser)
        self.superuser_auth = {
            'refresh': superuser_refresh,
            'access': str(superuser_refresh.access_token)
        }

        regular_user_refresh = RefreshToken.for_user(self.regular_user)
        self.regular_user_auth = {
            'refresh': regular_user_refresh,
            'access': str(regular_user_refresh.access_token)
        }

        # Initialize the API client with authentication headers
        self.client_superuser = APIClient()
        self.client_superuser.credentials(HTTP_AUTHORIZATION=f'Bearer {self.superuser_auth.get("access")}')

        self.client_regular_user = APIClient()
        self.client_regular_user.credentials(HTTP_AUTHORIZATION=f'Bearer {self.regular_user_auth.get("access")}')
    
    def test_create_superuser(self):
        data = {
            'email': 'test@test.com',
            'password': 'userpassword',
            'first_name': 'Regular',
            'last_name': 'User',
        }
        response = self.client_superuser.post(reverse('users-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
    
    def test_create_regular_user(self):
        data = {
            'email': 'regular@test.com',
            'password': 'userpassword',
            'first_name': 'Regular',
            'last_name': 'User',
        }
        response = self.client_regular_user.post(reverse('users-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_retrieve_user(self):
        response = self.client_regular_user.get(reverse('users-detail', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.regular_user.email)

    def test_update_user(self):
        data = {
            'email': 'test@test.com',
            'password': 'userpassword',
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
        }
        response = self.client_regular_user.put(reverse('users-detail', args=[self.regular_user.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.regular_user.id).first_name, 'UpdatedFirst')
        self.assertEqual(User.objects.get(id=self.regular_user.id).last_name, 'UpdatedLast')

    def test_partial_update_user(self):
        data = {
            'last_name': 'UpdatedLast',
        }
        response = self.client_regular_user.patch(reverse('users-detail', args=[self.regular_user.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.regular_user.id).last_name, 'UpdatedLast')

    def test_delete_user(self):
        response = self.client_regular_user.delete(reverse('users-detail', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)  # One user (superuser) remaining in the database
