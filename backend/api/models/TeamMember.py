from django.db import models

class TeamMember(models.Model):
    class_member_id = models.ForeignKey('ClassMember', on_delete=models.CASCADE, null=True)
    team_id = models.ForeignKey('Team', on_delete=models.CASCADE, null=True)

    LEADER = 0
    MEMBER = 1
    role_choices = (
        (LEADER, 'Leader'),
        (MEMBER, 'Member'),
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

    