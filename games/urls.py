from django.urls import path
from .views import (
    flashcard_view,
    weak_words_game,
    submit_weak_words_game,
    flashcard_filtered_view,
    flashcards_settings_mediator,
    weak_words_favorites_game,
)

urlpatterns = [
    path('flashcards/<int:playlist_id>/', flashcard_view, name='flashcards'),
    path('flashcards_settings_mediator/<int:playlist_id>/', flashcards_settings_mediator, name='flashcards_settings_mediator'),
    path('flashcards/<int:playlist_id>/filter/', flashcard_filtered_view, name='filtered_flashcards'),
    path('game/weak/', weak_words_game, name='weak_words_game'),
    path('game/weak/submit/', submit_weak_words_game, name='submit_weak_words_game'),
    path('game/favorites/', weak_words_favorites_game, name='weak_words_favorites_game'),
]
