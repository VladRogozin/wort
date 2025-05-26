from django.shortcuts import render, get_object_or_404
from playlist.models import Playlist
from django.shortcuts import get_object_or_404, render
from django.db.models import Case, When, F, Value as V, IntegerField, FloatField, ExpressionWrapper, Q


# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import F, ExpressionWrapper, IntegerField
from playlist.models import Word
from results.models import WordResult


def flashcard_view(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    words = list(playlist.words.values('id', 'word', 'translation', 'details', 'context'))

    return render(request, 'games/flashcards.html', {
        'playlist': playlist,
        'words': words,
    })


def flashcards_settings_mediator(request, playlist_id):
    return render(request, 'games/flashcards_settings_mediator.html', {
        'playlist': playlist_id,
    })


from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

@login_required
def flashcard_filtered_view(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    user = request.user

    percent_learned = int(request.GET.get('percent_learned', 50))
    limit = int(request.GET.get('limit', 20))

    # Получаем все слова из плейлиста
    all_words = playlist.words.all()

    filtered_words = []

    for word in all_words:
        result = WordResult.objects.filter(user=user, word=word).first()
        known = result.known_count if result else 0
        unknown = result.unknown_count if result else 0

        # Вычисляем percent_known по формуле
        raw_percent = (known - unknown) * 10
        percent_known = min(max(raw_percent, 0), 100)  # от 0 до 100

        # Фильтруем по проценту
        if percent_known <= percent_learned:
            filtered_words.append({
                'id': word.id,
                'word': word.word,
                'translation': word.translation,
                'details': word.details,
                'context': word.context,
                'percent_known': percent_known,
            })

    # Сортируем по percent_known по возрастанию
    filtered_words.sort(key=lambda x: x['percent_known'])

    # Ограничиваем по лимиту
    filtered_words = filtered_words[:limit]

    return render(request, 'games/flashcards.html', {
        'playlist': playlist,
        'words': filtered_words,
        'percent_learned': percent_learned,
        'limit': limit,
    })




@login_required
def weak_words_game(request):
    user = request.user

    # Получаем результаты с вычисленным прогрессом
    results = WordResult.objects.filter(user=user).annotate(
        progress=ExpressionWrapper((F('known_count') - F('unknown_count')) * 10, output_field=IntegerField())
    ).filter(progress__lt=40).order_by('progress')[:20]

    # Получаем объекты слов из результатов
    words_qs = [r.word for r in results]

    # Преобразуем объекты Word в список словарей с нужными полями
    words = []
    for word in words_qs:
        words.append({
            'id': word.id,
            'word': word.word,
            'translation': word.translation,
            'details': word.details,
            'context': word.context,
            # добавьте любые другие поля, которые нужны в JS
        })

    return render(request, 'games/weak_words_game.html', {
        'words': words,
    })


# views.py

from django.views.decorators.http import require_POST
from django.shortcuts import redirect

@require_POST
@login_required
def submit_weak_words_game(request):
    user = request.user
    for key, value in request.POST.items():
        if key.startswith('word_'):
            word_id = key.split('_')[1]
            try:
                word = Word.objects.get(id=word_id)
                result, created = WordResult.objects.get_or_create(user=user, word=word)
                if value == 'known':
                    result.known_count += 1
                elif value == 'unknown':
                    result.unknown_count += 1
                result.save()
            except Word.DoesNotExist:
                continue

    return redirect('weak_words_game')
