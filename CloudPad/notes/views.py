"""
Views for CloudPad note management.

This module handles HTTP requests for note operations including
viewing, saving, and loading notes.
"""

import logging
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import NoteService

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



# def upload_file(file_path, file):
#     bucket_name = "cloudpad-files"
#     note_id = "test"  # This should be dynamic based on your app

#     try:
#         # Ensure the file is stored inside a folder (like note_id/)
#         full_path = f"{note_id}/{os.path.basename(file_path)}"

#         res = supabase.storage.from_(bucket_name).upload(
#             full_path, file, file_options={"content-type": "application/octet-stream"}
#         )

#         return {"success": True, "message": "File uploaded successfully", "data": res}
#     except Exception as e:
#         return {"success": False, "error": str(e)}


# def list_files(request, note_id):
#     bucket_name = "cloudpad-files"
    
#     response = supabase.storage.from_(bucket_name).list(path=note_id)

#     if response:
#         files = [
#             {
#                 "file_name": file["name"],
#                 "file_url": f"{supabase_url}/storage/v1/object/public/{bucket_name}/{note_id}/{file['name']}",
#             }
#             for file in response
#         ]
#         return JsonResponse({"files": files})

#     return JsonResponse({"files": []})