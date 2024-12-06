from django.db import models

class MeetingCriteria(models.Model):
    meeting_id = models.ForeignKey('Meeting', on_delete=models.CASCADE)
    criteria_id = models.ForeignKey('Criteria', on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=3, decimal_places=2)
    