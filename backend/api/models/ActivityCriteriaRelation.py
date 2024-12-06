from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ActivityCriteriaRelation(models.Model):
    activity = models.ForeignKey('Activity', on_delete=models.CASCADE)
    activity_criteria = models.ForeignKey('ActivityCriteria', on_delete=models.CASCADE)
    strictness = models.IntegerField()  # Your additional field
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],  # Range 1 to 10
        default=0
    )
    activity_criteria_status = models.IntegerField(default=0)
    activity_criteria_feedback = models.CharField(max_length=8000, default='', blank=True, null=True)
    
    class Meta:
        unique_together = ('activity', 'activity_criteria')
