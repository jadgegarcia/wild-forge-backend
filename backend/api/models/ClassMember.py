from django.db import models

class ClassMember(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    class_id = models.ForeignKey('ClassRoom', on_delete=models.CASCADE, null=True)

    TEACHER = 0
    STUDENT = 1
    role_choices = (
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    )
    role = models.PositiveSmallIntegerField(choices=role_choices, null=True, blank=True)

    PENDING = 0
    ACCEPTED = 1
    status_choices = (
        (PENDING, 'pending'),
        (ACCEPTED, 'accepted'),
    )
    status = models.PositiveSmallIntegerField(choices=status_choices, null=True, blank=True)

    date_created = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now=True)
