from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Class, ClassMember, User
from api.serializers import ClassMemberSerializer
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

class ClassMembersTest(TestCase):
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
    
    def test_list_class_members(self):
        # Create a class
        new_class = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        # Create a class member
        class_member = ClassMember.objects.create(
            class_id=new_class,
            user_id=self.student,
            status='accepted'
        )

        # Get the class members as a student user
        response = self.client_student_user.get(reverse('class-members-list', kwargs={'class_pk': new_class.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ClassMemberSerializer([class_member], many=True).data)

    def test_list_class_members_unauthorized(self):
        # Create a class
        class1 = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        # Attempt to get class members as an unauthorized user
        response = self.client_teacher_user.get(reverse('class-members-list', kwargs={'class_pk': class1.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_class_member(self):
        # Create a class
        class1 = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        # Create a class member with a pending status
        class_member = ClassMember.objects.create(
            class_id=class1,
            user_id=self.student,
            status='pending'
        )

        # Accept the class member request as a teacher
        response = self.client_teacher_user.put(reverse('class-members-accept', kwargs={'class_pk': class1.id, 'pk': class_member.id}))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Verify that the class member status is now 'accepted'
        class_member.refresh_from_db()
        self.assertEqual(class_member.status, 'accepted')

    def test_accept_nonexistent_class_member(self):
        # Create a class
        class1 = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        # Attempt to accept a non-existent class member request
        response = self.client_teacher_user.put(reverse('class-members-accept', kwargs={'class_pk': class1.id, 'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_class_member(self):
        # Create a class
        class1 = Class.objects.create(
            name='Math 101',
            sections='A',
            schedule='MWF 9:00 AM - 10:00 AM'
        )

        # Create a class member
        class_member = ClassMember.objects.create(
            class_id=class1,
            user_id=self.student,
            status='accepted'
        )

        # Attempt to delete a class member as a student user (not allowed)
        response = self.client_student_user.delete(reverse('class-members-detail', kwargs={'class_pk': class1.id, 'pk': class_member.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Delete a class member as a teacher user
        response = self.client_teacher_user.delete(reverse('class-members-detail', kwargs={'class_pk': class1.id, 'pk': class_member.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the class member is deleted
        class_member_exists = ClassMember.objects.filter(pk=class_member.id).exists()
        self.assertFalse(class_member_exists)