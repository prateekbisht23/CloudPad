from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Note
# import os, supabase
# from dotenv import load_dotenv
# from django.views.decorators.csrf import csrf_exempt
# from supabase import create_client, Client


# Load environment variables
# load_dotenv()

# # Initialize Supabase client
# supabase_url = os.getenv("SUPABASE_URL")
# supabase_key = os.getenv("SUPABASE_KEY")

# supabase: Client = create_client(supabase_url, supabase_key)


# Create your views here.
def note_view(request, url_id):
    note, created = Note.objects.get_or_create(url_id = url_id)
    return render(request, 'note.html', {'note':note})

def save_note(request, url_id):
    if request.method == "POST":
        content = request.POST.get("content", "")
        note, created = Note.objects.get_or_create(url_id=url_id)
        note.content = content
        note.save()
        return JsonResponse({"status": "success", "content": note.content})
    
    return JsonResponse({"status": "failed"}, status=400)


def load_note(request, url_id):
    note, created = Note.objects.get_or_create(url_id=url_id)
    return JsonResponse({"content": note.content})



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