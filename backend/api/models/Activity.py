from django.db import models
from django.utils import timezone

class Activity(models.Model):
    classroom_id = models.ForeignKey('ClassRoom', on_delete=models.CASCADE, null=True)
    team_id = models.ManyToManyField('Team', null=True)
    activityCriteria_id = models.ManyToManyField('ActivityCriteria', through='ActivityCriteriaRelation', null=True)
    title = models.CharField(max_length=100, default="", null=False)
    description = models.TextField(max_length=10000, default="", null=False)
    instruction = models.TextField(max_length=10000, default="", null=False)
    submission_status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, default=timezone.now)
    evaluation = models.IntegerField(null=True)
    total_score = models.IntegerField(default=100, null=False)
    return_status = models.BooleanField(default=False)
    submission_attempts = models.IntegerField(default=0, null=False)
    spring_project = models.ForeignKey('SpringProject', on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def create_activity_from_template(cls, template):
        new_activity = cls(
            title=template.title,
            description=template.description,
            instruction=template.instructions,
            # Copy other fields from the template as needed
        )
        new_activity.save()
        return new_activity

    def __str__(self):
        return self.title