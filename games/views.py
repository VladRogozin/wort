from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, IntegerField
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from playlist.models import Playlist, Word, FavoriteWord
from results.models import WordResult


# Показывает карточки всех слов в плейлисте
def flashcard_view(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    words = list(playlist.words.values(
        'id', 'word', 'translation', 'details', 'context'
    ))

    return render(request, 'games/flashcards.html', {
        'playlist': playlist,
        'words': words,
    })


# Показывает страницу с настройками перед игрой
def flashcards_settings_mediator(request, playlist_id):
    return render(request, 'games/flashcards_settings_mediator.html', {
        'playlist': playlist_id,
    })


# Показывает отфильтрованные слова из плейлиста, которые пользователь знает хуже всего
@login_required
def flashcard_filtered_view(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    user = request.user

    percent_learned = int(request.GET.get('percent_learned', 50))
    limit = int(request.GET.get('limit', 20))
    show_word_first = request.GET.get('show_word_first') == 'on'

    all_words = playlist.words.all()
    filtered_words = []

    for word in all_words:
        result = WordResult.objects.filter(user=user, word=word).first()
        known = result.known_count if result else 0
        unknown = result.unknown_count if result else 0

        raw_percent = (known - unknown) * 10
        percent_known = min(max(raw_percent, 0), 100)

        if percent_known <= percent_learned:
            filtered_words.append({
                'id': word.id,
                'word': word.word,
                'translation': word.translation,
                'details': word.details,
                'context': word.context,
                'percent_known': percent_known,
            })

    filtered_words.sort(key=lambda x: x['percent_known'])
    filtered_words = filtered_words[:limit]

    return render(request, 'games/flashcards.html', {
        'playlist': playlist,
        'words': filtered_words,
        'percent_learned': percent_learned,
        'limit': limit,
        'show_word_first': show_word_first,
    })


# Показывает слабые (плохо выученные) слова пользователя в виде карточек
@login_required
def weak_words_game(request):
    user = request.user

    results = WordResult.objects.filter(user=user).annotate(
        progress=ExpressionWrapper(
            (F('known_count') - F('unknown_count')) * 10,
            output_field=IntegerField()
        )
    ).filter(progress__lt=40).order_by('progress')[:20]

    words_qs = [r.word for r in results]
    words = []

    for word in words_qs:
        playlist = word.playlists
        words.append({
            'id': word.id,
            'word': word.word,
            'translation': word.translation,
            'details': word.details,
            'context': word.context,
            'playlist': {
                'title': playlist.title if playlist else "Без плейлиста",
                'color': playlist.color if playlist else "#999999"
            }
        })

    return render(request, 'games/weak_words_game.html', {
        'words': words,
    })


from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from playlist.models import Word
from results.models import WordResult

@require_POST
@login_required
def submit_weak_words_game(request):
    user = request.user

    for key, value in request.POST.items():
        if key.startswith('word_'):
            word_id = key.split('_')[1]
            try:
                word = Word.objects.get(id=word_id)
                result, _ = WordResult.objects.get_or_create(user=user, word=word)
                value = value.strip().lower()

                # Обновляем known_count и unknown_count без ограничений
                if value == 'known':
                    result.known_count += 1
                    # Обновляем current_result с ограничением
                    if result.current_result is None:
                        result.current_result = 0
                    if result.current_result < 10:
                        result.current_result += 1
                elif value == 'unknown':
                    result.unknown_count += 1
                    # Обновляем current_result с ограничением
                    if result.current_result is None:
                        result.current_result = 0
                    if result.current_result > 0:
                        result.current_result -= 1

                result.save()
            except Word.DoesNotExist:
                continue

    return redirect('weak_words_game')



# Игра по словам, добавленным в избранное
@login_required
def weak_words_favorites_game(request):
    # Получить все избранные слова текущего пользователя
    favorites = FavoriteWord.objects.filter(user=request.user).select_related('word')

    # Извлечь объекты Word
    words = [fav.word for fav in favorites]

    # Подготовить список слов в формате, подходящем для шаблона
    word_data = [
        {
            'id': word.id,
            'word': word.word,
            'translation': word.translation,
            'details': word.details,
            'context': word.context
        }
        for word in words
    ]

    return render(request, 'games/favorites_game.html', {
        'words': word_data,
        'debug': request.GET.get('debug') == '1'
    })
