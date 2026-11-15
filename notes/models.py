from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid


class ActiveNoteManager(models.Manager):
    """Custom manager to filter out soft-deleted notes"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def active(self):
        """Get only active (non-deleted, non-expired) notes"""
        expiry_threshold = timezone.now() - timedelta(days=7)
        return self.get_queryset().filter(last_accessed__gte=expiry_threshold)


class Note(models.Model):
    """
    Model representing a note/pad with content and file attachments.
    
    Notes are identified by unique URL IDs and support soft deletion
    with automatic expiration after 7 days of inactivity.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the note"
    )
    url_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="URL-safe identifier for accessing the note"
    )
    content = models.TextField(
        blank=True,
        null=True,
        default='',
        help_text="Text content of the note"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when note was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when note was last modified"
    )
    last_accessed = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when note was last accessed (for auto-deletion)"
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Soft deletion flag"
    )
    
    # Managers
    objects = models.Manager()  # Default manager
    active_objects = ActiveNoteManager()  # Custom manager for active notes
    
    class Meta:
        db_table = 'notes'
        ordering = ['-last_accessed']
        indexes = [
            models.Index(fields=['url_id', 'is_deleted']),
            models.Index(fields=['last_accessed', 'is_deleted']),
        ]
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
    
    def __str__(self):
        return f"Note: {self.url_id}"
    
    def is_expired(self, days=7):
        """
        Check if the note has expired based on last access time.
        
        Args:
            days: Number of days before expiration (default: 7)
        
        Returns:
            bool: True if note is expired
        """
        if not self.last_accessed:
            return False
        
        expiry_threshold = timezone.now() - timedelta(days=days)
        return self.last_accessed < expiry_threshold
    
    def mark_as_deleted(self, save=True):
        """
        Soft delete the note.
        
        Args:
            save: Whether to save the model immediately (default: True)
        """
        self.is_deleted = True
        if save:
            self.save(update_fields=['is_deleted'])
    
    def touch_access(self):
        """
        Update the last_accessed timestamp to current time.
        This prevents the note from being auto-deleted.
        """
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])
    
    def get_age_in_days(self):
        """
        Get the age of the note in days since creation.
        
        Returns:
            int: Number of days since creation
        """
        return (timezone.now() - self.created_at).days
    
    def get_inactive_days(self):
        """
        Get the number of days since last access.
        
        Returns:
            int: Number of days since last access
        """
        return (timezone.now() - self.last_accessed).days
    
    @property
    def is_active(self):
        """Check if note is active (not deleted and not expired)"""
        return not self.is_deleted and not self.is_expired()
