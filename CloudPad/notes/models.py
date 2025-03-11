from django.db import models
import uuid

class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url_id = models.TextField(max_length=255, unique=True, null=False, blank=False)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)  # File storage
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notes'
