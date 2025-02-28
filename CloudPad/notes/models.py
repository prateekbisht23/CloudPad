from django.db import models

# Create your models here.
class Note(models.Model):
    url_id = models.CharField(max_length=50, unique=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url_id