from django.urls import path
from .views import note_view, save_note, load_note

urlpatterns = [
    path('<str:url_id>/', note_view, name='note_view'),
    path('<str:url_id>/save/', save_note, name="save_note"),
    path("<str:url_id>/load/", load_note, name="load_note"),
]