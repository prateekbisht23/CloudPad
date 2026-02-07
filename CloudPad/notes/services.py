"""
Service layer for CloudPad note operations.

This module contains business logic for note management,
separating it from the view layer for better organization
and testability.
"""

import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Note
from .validators import validate_url_id, validate_note_content

logger = logging.getLogger(__name__)


class NoteService:
    """Service class for note-related business logic"""
    
    @staticmethod
    def get_or_create_note(url_id):
        """
        Get an existing note or create a new one.
        
        Args:
            url_id: URL identifier for the note
        
        Returns:
            tuple: (Note instance, created boolean)
        
        Raises:
            ValidationError: If URL ID is invalid
        """
        try:
            # Validate URL ID
            validated_url_id = validate_url_id(url_id)
            
            # Get or create the note
            note, created = Note.active_objects.get_or_create(
                url_id=validated_url_id,
                defaults={'content': ''}
            )
            
            # Touch access time to prevent expiration
            if not created:
                note.touch_access()
            
            logger.info(
                f"Note {'created' if created else 'retrieved'}: {url_id}",
                extra={'url_id': url_id, 'note_id': str(note.id), 'was_created': created}
            )
            
            return note, created
            
        except ValidationError as e:
            logger.warning(
                f"Invalid URL ID attempted: {url_id}",
                extra={'url_id': url_id, 'error': str(e)}
            )
            raise
        except Exception as e:
            logger.error(
                f"Error getting/creating note: {url_id}",
                extra={'url_id': url_id, 'error': str(e)},
                exc_info=True
            )
            raise
    
    @staticmethod
    @transaction.atomic
    def save_note_content(url_id, content):
        """
        Save content to a note.
        
        Args:
            url_id: URL identifier for the note
            content: Content to save
        
        Returns:
            Note: Updated note instance
        
        Raises:
            ValidationError: If content or URL ID is invalid
        """
        try:
            # Validate content
            validated_content = validate_note_content(content)
            
            # Get or create note
            note, created = NoteService.get_or_create_note(url_id)
            
            # Update content
            note.content = validated_content
            note.save(update_fields=['content', 'updated_at'])
            
            # Touch access time
            note.touch_access()
            
            logger.info(
                f"Note content saved: {url_id}",
                extra={
                    'url_id': url_id,
                    'note_id': str(note.id),
                    'content_length': len(validated_content)
                }
            )
            
            return note
            
        except ValidationError as e:
            logger.warning(
                f"Invalid content for note: {url_id}",
                extra={'url_id': url_id, 'error': str(e)}
            )
            raise
        except Exception as e:
            logger.error(
                f"Error saving note content: {url_id}",
                extra={'url_id': url_id, 'error': str(e)},
                exc_info=True
            )
            raise
    
    @staticmethod
    def get_note_content(url_id):
        """
        Get content from a note.
        
        Args:
            url_id: URL identifier for the note
        
        Returns:
            str: Note content
        
        Raises:
            ValidationError: If URL ID is invalid
        """
        try:
            # Get or create note
            note, created = NoteService.get_or_create_note(url_id)
            
            logger.info(
                f"Note content retrieved: {url_id}",
                extra={
                    'url_id': url_id,
                    'note_id': str(note.id),
                    'content_length': len(note.content or '')
                }
            )
            
            return note.content or ''
            
        except Exception as e:
            logger.error(
                f"Error retrieving note content: {url_id}",
                extra={'url_id': url_id, 'error': str(e)},
                exc_info=True
            )
            raise
    
    @staticmethod
    def delete_note(url_id):
        """
        Soft delete a note.
        
        Args:
            url_id: URL identifier for the note
        
        Returns:
            bool: True if note was deleted, False if not found
        """
        try:
            validated_url_id = validate_url_id(url_id)
            
            try:
                note = Note.active_objects.get(url_id=validated_url_id)
                note.mark_as_deleted()
                
                logger.info(
                    f"Note soft deleted: {url_id}",
                    extra={'url_id': url_id, 'note_id': str(note.id)}
                )
                
                return True
                
            except Note.DoesNotExist:
                logger.warning(
                    f"Attempted to delete non-existent note: {url_id}",
                    extra={'url_id': url_id}
                )
                return False
                
        except Exception as e:
            logger.error(
                f"Error deleting note: {url_id}",
                extra={'url_id': url_id, 'error': str(e)},
                exc_info=True
            )
            raise
    
    @staticmethod
    def get_note_stats(url_id):
        """
        Get statistics about a note.
        
        Args:
            url_id: URL identifier for the note
        
        Returns:
            dict: Note statistics
        """
        try:
            note, _ = NoteService.get_or_create_note(url_id)
            
            return {
                'url_id': note.url_id,
                'created_at': note.created_at,
                'updated_at': note.updated_at,
                'last_accessed': note.last_accessed,
                'age_days': note.get_age_in_days(),
                'inactive_days': note.get_inactive_days(),
                'is_expired': note.is_expired(),
                'is_active': note.is_active,
                'content_length': len(note.content or ''),
            }
            
        except Exception as e:
            logger.error(
                f"Error getting note stats: {url_id}",
                extra={'url_id': url_id, 'error': str(e)},
                exc_info=True
            )
            raise
