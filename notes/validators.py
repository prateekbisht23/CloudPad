"""
Validators for CloudPad application.

This module contains validators for user input including URL IDs,
content sanitization, and file upload validation.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import bleach


# Allowed HTML tags for content sanitization
ALLOWED_TAGS = []  # No HTML allowed by default
ALLOWED_ATTRIBUTES = {}


def validate_url_id(url_id):
    """
    Validate URL ID to prevent injection attacks and ensure URL safety.
    
    Args:
        url_id: The URL identifier to validate
    
    Raises:
        ValidationError: If URL ID is invalid
    
    Returns:
        str: The validated URL ID
    """
    if not url_id:
        raise ValidationError("URL ID cannot be empty")
    
    if len(url_id) > 255:
        raise ValidationError("URL ID must be less than 255 characters")
    
    # Allow alphanumeric, hyphens, underscores only
    if not re.match(r'^[a-zA-Z0-9_-]+$', url_id):
        raise ValidationError(
            "URL ID can only contain letters, numbers, hyphens, and underscores"
        )
    
    # Prevent potential SQL injection patterns
    dangerous_patterns = ['--', ';', 'DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT']
    url_id_upper = url_id.upper()
    for pattern in dangerous_patterns:
        if pattern in url_id_upper:
            raise ValidationError("URL ID contains invalid characters or patterns")
    
    return url_id


def sanitize_content(content):
    """
    Sanitize note content to prevent XSS attacks.
    
    Args:
        content: The content to sanitize
    
    Returns:
        str: Sanitized content
    """
    if not content:
        return ''
    
    # Remove any HTML tags and return plain text
    # Using bleach for additional security
    sanitized = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return sanitized.strip()


def validate_file_upload(file):
    """
    Validate uploaded file for size and type.
    
    Args:
        file: The uploaded file object
    
    Raises:
        ValidationError: If file is invalid
    """
    # Maximum file size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f"File size must not exceed 10MB. Your file is {file.size / (1024 * 1024):.2f}MB"
        )
    
    # Allowed file types
    ALLOWED_CONTENT_TYPES = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/gif',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ]
    
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError(
            f"File type '{file.content_type}' is not allowed. "
            f"Allowed types: PDF, JPEG, PNG, GIF, TXT, DOC, DOCX"
        )
    
    # Check file extension
    ALLOWED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.doc', '.docx']
    file_extension = '.' + file.name.split('.')[-1].lower() if '.' in file.name else ''
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File extension '{file_extension}' is not allowed"
        )


def validate_note_content(content):
    """
    Validate note content for length and format.
    
    Args:
        content: The note content to validate
    
    Raises:
        ValidationError: If content is invalid
    
    Returns:
        str: Validated content
    """
    if content is None:
        return ''
    
    # Maximum content size: 1MB of text
    MAX_CONTENT_LENGTH = 1024 * 1024
    
    if len(content) > MAX_CONTENT_LENGTH:
        raise ValidationError(
            f"Content is too large. Maximum size is {MAX_CONTENT_LENGTH / 1024:.0f}KB"
        )
    
    # Sanitize for XSS
    return sanitize_content(content)
