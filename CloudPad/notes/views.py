"""
Views for CloudPad note management.

This module handles HTTP requests for note operations including
viewing, saving, loading notes, and proxied file operations
using the Supabase service role key (bypasses RLS).
"""

import logging
import os
import requests as http_requests
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import NoteService

# ---------------------------------------------------------------------------
# Supabase Storage helpers (server-side, uses service role key → bypasses RLS)
# ---------------------------------------------------------------------------
SUPABASE_BUCKET = "cloudpad-files"

def _supabase_headers():
    """Return auth headers using the service role key."""
    service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    return {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
    }

def _storage_base():
    return f"{os.getenv('SUPABASE_URL')}/storage/v1"

logger = logging.getLogger(__name__)


def home(request):
    """Render the home page."""
    return render(request, 'home.html')


def about(request):
    """Render the about page."""
    return render(request, 'about.html')


@ensure_csrf_cookie
@require_http_methods(["GET"])
def note_view(request, url_id):
    """
    Display a note by URL ID.
    
    Creates a new note if it doesn't exist. Supabase credentials
    are passed for client-side file operations (this is a known
    limitation - ideally file uploads should go through backend).
    
    Args:
        request: HTTP request object
        url_id: URL identifier for the note
    
    Returns:
        Rendered template or error response
    """
    try:
        # Get or create note using service layer
        note, created = NoteService.get_or_create_note(url_id)
        
        # Pass minimal context to template
        # Note: SUPABASE credentials are still needed for client-side file upload
        # This is a security concern that should be addressed by moving
        # file uploads to backend in future iterations
        context = {
            'note': note,
            'SUPABASE_URL': os.getenv('SUPABASE_URL'),  # Still needed for file uploads
            'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),  # Still needed for file uploads
            'BASE_URL': os.getenv('BASE_URL', 'http://localhost:8000/'),
            'YJS_WS_URL': os.getenv('YJS_WS_URL', 'ws://localhost:1234'),
        }
        
        logger.info(
            f"Note view accessed: {url_id}",
            extra={'url_id': url_id, 'was_created': created}
        )
        
        return render(request, 'note.html', context)
        
    except ValidationError as e:
        logger.warning(
            f"Invalid URL ID in note view: {url_id}",
            extra={'url_id': url_id, 'error': str(e)}
        )
        return render(
            request,
            'error.html',
            {'error_message': f"Invalid URL: {str(e)}"},
            status=400
        )
    except Exception as e:
        logger.error(
            f"Error in note view: {url_id}",
            extra={'url_id': url_id, 'error': str(e)},
            exc_info=True
        )
        return render(
            request,
            'error.html',
            {'error_message': 'An unexpected error occurred. Please try again.'},
            status=500
        )


@require_POST
def save_note(request, url_id):
    """
    Save note content via AJAX (supports JSON and Form Data).
    """
    try:
        # Try to parse JSON body first
        import json
        content = ""
        
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                content = data.get("content", "")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received for {url_id}")
        else:
            # Fallback to Form Data
            content = request.POST.get("content", "")

        # Log what we received (truncated for sanity)
        logger.info(f"Received save request for {url_id}. Content length: {len(content)}")

        # Save using service layer
        note = NoteService.save_note_content(url_id, content)
        
        return JsonResponse({
            "status": "success",
            "content": note.content,
            "message": "Note saved successfully"
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
        
    except Exception as e:
        logger.error(f"Error saving note: {e}", exc_info=True)
        return JsonResponse({"status": "error", "message": "Server error"}, status=500)


@require_http_methods(["GET"])
def load_note(request, url_id):
    """
    Load note content via AJAX.
    
    Args:
        request: HTTP request object
        url_id: URL identifier for the note
    
    Returns:
        JSON response with note content
    """
    try:
        # Get content using service layer
        content = NoteService.get_note_content(url_id)
        
        logger.info(
            f"Note loaded successfully: {url_id}",
            extra={'url_id': url_id, 'content_length': len(content)}
        )
        
        return JsonResponse({
            "status": "success",
            "content": content
        })
        
    except ValidationError as e:
        logger.warning(
            f"Validation error loading note: {url_id}",
            extra={'url_id': url_id, 'error': str(e)}
        )
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
        
    except Exception as e:
        logger.error(
            f"Error loading note: {url_id}",
            extra={'url_id': url_id, 'error': str(e)},
            exc_info=True
        )
        return JsonResponse({
            "status": "error",
            "message": "Failed to load note. Please try again."
        }, status=500)




@require_POST
def upload_file(request, url_id):
    """
    Proxy file upload to Supabase Storage using the service role key.
    This bypasses Supabase RLS so no client-side privileged key is needed.
    """
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"error": "No file provided"}, status=400)

    # Validate file size (10 MB max)
    MAX_SIZE = 10 * 1024 * 1024
    if file.size > MAX_SIZE:
        return JsonResponse({"error": "File size exceeds 10MB limit"}, status=400)

    file_path = f"{url_id}/{file.name}"
    url = f"{_storage_base()}/object/{SUPABASE_BUCKET}/{file_path}"

    try:
        resp = http_requests.post(
            url,
            headers={**_supabase_headers(), "x-upsert": "true"},
            data=file.read(),
        )
        if resp.status_code in (200, 201):
            public_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"
            logger.info(f"File uploaded: {file_path}")
            return JsonResponse({"status": "success", "url": public_url, "name": file.name})
        else:
            logger.error(f"Supabase upload failed: {resp.status_code} {resp.text}")
            return JsonResponse({"error": resp.json().get("message", "Upload failed")}, status=resp.status_code)
    except Exception as e:
        logger.error(f"File upload error: {e}", exc_info=True)
        return JsonResponse({"error": "Upload failed"}, status=500)


@require_http_methods(["GET"])
def list_files(request, url_id):
    """
    List files in a note's folder from Supabase Storage via service role key.
    """
    url = f"{_storage_base()}/object/list/{SUPABASE_BUCKET}"
    try:
        resp = http_requests.post(
            url,
            headers={**_supabase_headers(), "Content-Type": "application/json"},
            json={"prefix": f"{url_id}/", "limit": 100, "offset": 0},
        )
        if resp.status_code == 200:
            files = resp.json()
            supabase_url = os.getenv("SUPABASE_URL")
            result = [
                {
                    "name": f["name"],
                    "size": f.get("metadata", {}).get("size", 0),
                    "url": f"{supabase_url}/storage/v1/object/public/{SUPABASE_BUCKET}/{url_id}/{f['name']}",
                }
                for f in files
                if f.get("name") and f["name"] != ".placeholder"
            ]
            return JsonResponse({"files": result})
        else:
            return JsonResponse({"files": []})
    except Exception as e:
        logger.error(f"List files error: {e}", exc_info=True)
        return JsonResponse({"files": []})


@require_POST
def delete_file(request, url_id, file_name):
    """
    Delete a file from Supabase Storage via service role key.
    """
    file_path = f"{url_id}/{file_name}"
    url = f"{_storage_base()}/object/{SUPABASE_BUCKET}"
    try:
        resp = http_requests.delete(
            url,
            headers={**_supabase_headers(), "Content-Type": "application/json"},
            json={"prefixes": [file_path]},
        )
        if resp.status_code == 200:
            logger.info(f"File deleted: {file_path}")
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"error": "Delete failed"}, status=resp.status_code)
    except Exception as e:
        logger.error(f"Delete file error: {e}", exc_info=True)
        return JsonResponse({"error": "Delete failed"}, status=500)