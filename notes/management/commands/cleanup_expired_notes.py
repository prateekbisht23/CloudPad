"""
Django management command to clean up expired notes.

This command should be run periodically (e.g., via cron job) to:
1. Soft delete notes that haven't been accessed in 7 days
2. Hard delete notes that were soft deleted more than 30 days ago

Usage:
    python manage.py cleanup_expired_notes
    python manage.py cleanup_expired_notes --dry-run
    python manage.py cleanup_expired_notes --days=14
"""

import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from notes.models import Note

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up expired notes (soft delete after 7 days, hard delete after 30 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days of inactivity before soft deletion (default: 7)',
        )
        parser.add_argument(
            '--hard-delete-days',
            type=int,
            default=30,
            help='Number of days after soft deletion before hard deletion (default: 30)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        expiry_days = options['days']
        hard_delete_days = options['hard_delete_days']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Calculate thresholds
        soft_delete_threshold = timezone.now() - timedelta(days=expiry_days)
        hard_delete_threshold = timezone.now() - timedelta(days=hard_delete_days)
        
        # Soft delete expired notes
        expired_notes = Note.objects.filter(
            is_deleted=False,
            last_accessed__lt=soft_delete_threshold
        )
        
        expired_count = expired_notes.count()
        
        if expired_count > 0:
            self.stdout.write(
                f'Found {expired_count} notes to soft delete '
                f'(inactive for {expiry_days}+ days)'
            )
            
            if not dry_run:
                for note in expired_notes:
                    note.mark_as_deleted()
                    logger.info(
                        f'Soft deleted expired note: {note.url_id}',
                        extra={
                            'note_id': str(note.id),
                            'url_id': note.url_id,
                            'inactive_days': note.get_inactive_days()
                        }
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully soft deleted {expired_count} expired notes')
                )
            else:
                for note in expired_notes:
                    self.stdout.write(
                        f'  Would soft delete: {note.url_id} '
                        f'(last accessed: {note.last_accessed}, '
                        f'{note.get_inactive_days()} days ago)'
                    )
        else:
            self.stdout.write(self.style.SUCCESS('No expired notes found for soft deletion'))
        
        # Hard delete old soft-deleted notes
        old_deleted_notes = Note.objects.filter(
            is_deleted=True,
            updated_at__lt=hard_delete_threshold
        )
        
        hard_delete_count = old_deleted_notes.count()
        
        if hard_delete_count > 0:
            self.stdout.write(
                f'Found {hard_delete_count} soft-deleted notes to permanently delete '
                f'(deleted {hard_delete_days}+ days ago)'
            )
            
            if not dry_run:
                deleted_urls = list(old_deleted_notes.values_list('url_id', flat=True))
                old_deleted_notes.delete()
                
                for url_id in deleted_urls:
                    logger.info(
                        f'Hard deleted old note: {url_id}',
                        extra={'url_id': url_id}
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully hard deleted {hard_delete_count} old soft-deleted notes'
                    )
                )
            else:
                for note in old_deleted_notes:
                    self.stdout.write(
                        f'  Would hard delete: {note.url_id} '
                        f'(soft deleted: {note.updated_at})'
                    )
        else:
            self.stdout.write(
                self.style.SUCCESS('No old soft-deleted notes found for hard deletion')
            )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCleanup summary:'
                f'\n  - Notes to soft delete: {expired_count}'
                f'\n  - Notes to hard delete: {hard_delete_count}'
                f'\n  - Mode: {"DRY RUN" if dry_run else "LIVE"}'
            )
        )
