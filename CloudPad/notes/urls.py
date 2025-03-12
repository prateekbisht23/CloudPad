from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import note_view, save_note, load_note

urlpatterns = [
    path("<str:url_id>/", note_view, name="note_view"),
    path("<str:url_id>/save/", save_note, name="save_note"),
    path("<str:url_id>/load/", load_note, name="load_note"),
    # path("<str:url_id>/upload/", upload_file, name="upload_file"),  # File Upload
    # path("<str:url_id>/files/", get_uploaded_files, name="get_uploaded_files"),  # Fetch Files
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
