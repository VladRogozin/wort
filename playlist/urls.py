from django.urls import path
from . import views

urlpatterns = [
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlists/en/', views.playlist_list, {'language': 'EN'}, name='playlist_list_en'),
    path('playlists/de/', views.playlist_list, {'language': 'DE'}, name='playlist_list_de'),

    path('playlists/create/', views.create_playlist, name='create_playlist'),
    path('playlists/edit/<int:pk>/', views.edit_playlist, name='edit_playlist'),
    path('playlists/delete/<int:pk>/', views.delete_playlist, name='delete_playlist'),

    path('words/create/', views.create_word, name='create_word'),
    path('words/edit/<int:pk>/', views.edit_word, name='edit_word'),
    path('words/delete/<int:pk>/', views.delete_word, name='delete_word'),

    path('playlists/<int:pk>/', views.playlist_detail, name='playlist_detail'),
    path('playlists/<int:playlist_pk>/remove-word/<int:word_pk>/', views.remove_word_from_playlist,
         name='remove_word_from_playlist'),
    path('upload-json/', views.bulk_upload_words, name='bulk_upload_words'),
    path('words/add-to-favorites/<int:word_pk>/', views.add_word_to_favorites, name='add_word_to_favorites'),
    path('favorites/list/', views.favorites_list, name='favorites_list'),
]
