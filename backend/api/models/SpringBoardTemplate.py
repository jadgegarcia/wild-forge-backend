from django.db import models


class SpringBoardTemplate(models.Model):
    title = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    rules = models.TextField()
    description = models.TextField()
    date_created = models.DateTimeField(auto_now=True)
