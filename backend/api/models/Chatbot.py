from django.db import models

class Chatbot(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    messages = models.ManyToManyField('Message')
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    