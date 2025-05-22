from django.urls import path
from .views import flashcard_view, weak_words_game, submit_weak_words_game

urlpatterns = [
    path('flashcards/<int:playlist_id>/', flashcard_view, name='flashcards'),
    path('game/weak/', weak_words_game, name='weak_words_game'),
    path('game/weak/submit/', submit_weak_words_game, name='submit_weak_words_game'),

]
