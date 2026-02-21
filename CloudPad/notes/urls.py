from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import note_view, save_note, load_note, home, about, upload_file, list_files, delete_file

urlpatterns = [
    path('', home, name='home'),
    path("about/", about, name='about'),
    path("<str:url_id>/", note_view, name="note_view"),
    path("<str:url_id>/save/", save_note, name="save_note"),
    path("<str:url_id>/load/", load_note, name="load_note"),
    path("<str:url_id>/upload/", upload_file, name="upload_file"),
    path("<str:url_id>/files/", list_files, name="list_files"),
    path("<str:url_id>/files/<str:file_name>/delete/", delete_file, name="delete_file"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
