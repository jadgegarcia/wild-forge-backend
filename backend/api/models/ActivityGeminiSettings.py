from django.db import models

class ActivityGeminiSettings(models.Model):
    api_key = models.CharField(max_length=255)  # Adjust max_length as needed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings (API Key: {self.api_key})"