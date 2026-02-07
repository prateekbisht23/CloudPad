"""
Tests for Note model.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from notes.models import Note


class NoteModelTestCase(TestCase):
    """Test cases for the Note model"""

    def setUp(self):
        """Set up test data"""
        self.note = Note.objects.create(
            url_id='test-note',
            content='Test content'
        )

    def test_note_creation(self):
        """Test that a note can be created"""
        self.assertIsNotNone(self.note.id)
        self.assertEqual(self.note.url_id, 'test-note')
        self.assertEqual(self.note.content, 'Test content')
        self.assertFalse(self.note.is_deleted)

    def test_note_str(self):
        """Test string representation"""
        self.assertEqual(str(self.note), 'Note: test-note')

    def test_is_expired_fresh_note(self):
        """Test that a fresh note is not expired"""
        self.assertFalse(self.note.is_expired())

    def test_is_expired_old_note(self):
        """Test that an old note is expired"""
        # Set last_accessed to 8 days ago
        self.note.last_accessed = timezone.now() - timedelta(days=8)
        self.note.save()
        self.assertTrue(self.note.is_expired())

    def test_mark_as_deleted(self):
        """Test soft deletion"""
        self.note.mark_as_deleted()
        self.assertTrue(self.note.is_deleted)

    def test_touch_access(self):
        """Test updating last_accessed timestamp"""
        old_time = self.note.last_accessed
        # Wait a bit
        import time
        time.sleep(0.1)
        self.note.touch_access()
        self.assertGreater(self.note.last_accessed, old_time)

    def test_is_active(self):
        """Test is_active property"""
        self.assertTrue(self.note.is_active)
        
        # Mark as deleted
        self.note.mark_as_deleted()
        self.assertFalse(self.note.is_active)

    def test_active_manager(self):
        """Test custom manager filters deleted notes"""
        # Create a deleted note
        deleted_note = Note.objects.create(
            url_id='deleted-note',
            content='Deleted'
        )
        deleted_note.mark_as_deleted()

        # Active manager should not return deleted notes
        active_notes = Note.active_objects.all()
        self.assertIn(self.note, active_notes)
        self.assertNotIn(deleted_note, active_notes)

    def test_get_age_in_days(self):
        """Test getting note age"""
        age = self.note.get_age_in_days()
        self.assertIsInstance(age, int)
        self.assertGreaterEqual(age, 0)

    def test_get_inactive_days(self):
        """Test getting inactive days"""
        days = self.note.get_inactive_days()
        self.assertIsInstance(days, int)
        self.assertGreaterEqual(days, 0)
