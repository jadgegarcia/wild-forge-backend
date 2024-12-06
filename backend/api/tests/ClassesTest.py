from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from api.models import Class, User, ClassMember
from rest_framework_simplejwt.tokens import RefreshToken

class ClassesTest(TestCase):
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
        self.teacher = User.objects.create(
            email='teacher@example.com',
            password='userpassword',
            first_name='Teacher',
            last_name='User',
            is_staff=True
        )

        self.student = User.objects.create(
            email='student@example.com',
            password='userpassword',
            first_name='Student',
            last_name='User'
        )


        # Create JWT tokens for authentication

        superuser_refresh = RefreshToken.for_user(self.superuser)
        self.superuser_auth = {
            'refresh': superuser_refresh,
            'access': str(superuser_refresh.access_token)
        }

        teacher_refresh = RefreshToken.for_user(self.teacher)
        self.teacher_auth = {
            'refresh': teacher_refresh,
            'access': str(teacher_refresh.access_token)
        }

        student_refresh = RefreshToken.for_user(self.student)
        self.student_auth = {
            'refresh': student_refresh,
            'access': str(student_refresh.access_token)
        }

        # Initialize the API client with authentication headers
        self.client_superuser = APIClient()
        self.client_superuser.credentials(HTTP_AUTHORIZATION=f'Bearer {self.superuser_auth.get("access")}')

        self.client_teacher_user = APIClient()
        self.client_teacher_user.credentials(HTTP_AUTHORIZATION=f'Bearer {self.teacher_auth.get("access")}')

        self.client_student_user = APIClient()
        self.client_student_user.credentials(HTTP_AUTHORIZATION=f'Bearer {self.student_auth.get("access")}')

    def test_create_class_as_teacher(self):
        url = reverse('class-list')
        data = {
            'name': 'Math 101',
            'sections': 'A',
            'schedule': 'MWF 9:00 AM - 10:00 AM',
            'class_code': '12345678'
        }

        response = self.client_teacher_user.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_class_success(self):
        new_class = Class.objects.create(
        name='Math 101',
        sections='A',
        schedule='MWF 9:00 AM - 10:00 AM'
        )

        class_member = ClassMember.objects.create(
            user_id=self.student,
            class_id=new_class,
            role='s',  
            status='accepted'
        )

        # Ensure that the student user is authenticated
        self.client_student_user.force_authenticate(user=self.student)
        url = reverse('class-detail', args=[new_class.id])
        response = self.client_student_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_class_not_found(self):
        url = reverse('class-detail', args=[999])
        response = self.client_student_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_class_unauthorized(self):
        # Create a new student user (not part of the class)
        unauthorized_user = User.objects.create(
            email='unauthorized@example.com',
            password='userpassword',
            first_name='Unauthorized',
            last_name='User'
        )

        new_class = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        unauthorized_refresh = RefreshToken.for_user(unauthorized_user)
        unauthorized_auth = {
            'refresh': str(unauthorized_refresh),
            'access': str(unauthorized_refresh.access_token)
        }

        self.client_unauthorized = APIClient()
        self.client_unauthorized.credentials(HTTP_AUTHORIZATION=f'Bearer {unauthorized_auth["access"]}')

        url = reverse('class-detail', args=[new_class.id])
        response = self.client_unauthorized.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_classes_as_superuser(self):
        response = self.client_superuser.get(reverse('class-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_classes_as_teacher(self):
        response = self.client_teacher_user.get(reverse('class-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_classes_as_user(self):
        response = self.client_student_user.get(reverse('class-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_update_class(self):
        new_class = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        url = reverse('class-detail', args=[new_class.id])
        data = {
            'name': 'Math 101',
            'sections': 'B',
            'schedule': 'MWF 9:00 AM - 10:00 AM'
        }

        response = self.client_teacher_user.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_partial_update_class(self):
        new_class = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        url = reverse('class-detail', args=[new_class.id])
        data = {
            'sections': 'B'
        }

        response = self.client_teacher_user.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_delete_class(self):
        new_class = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        url = reverse('class-detail', args=[new_class.id])

        response = self.client_teacher_user.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)