import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from results.models import GameResult, WordResult

from .forms import PlaylistForm, WordBulkUploadForm, WordForm
from .models import FavoriteWord, Playlist, Word


from django.utils.timesince import timesince
from results.models import WordResult, GameResult
from django.utils.timezone import now

@login_required
def playlist_list(request, language=None):
    color_filter = request.GET.get('color')
    playlists = Playlist.objects.filter(user=request.user)

    if language in ['EN', 'DE']:
        playlists = playlists.filter(language=language)

    if color_filter:
        playlists = playlists.filter(color=color_filter)

    # Добавим дополнительную информацию
    for playlist in playlists:
        words = playlist.words.all()
        total_words = words.count()

        # Прогресс
        word_results = WordResult.objects.filter(user=request.user, word__in=words).exclude(current_result__isnull=True)
        total_words = words.count()
        result_count = word_results.count()
        sum_results = sum(r.current_result for r in word_results)  # сумма current_result, где current_result от 0 до 10
        percent = int((sum_results / result_count) * 10) if result_count else 0  # умножаем на 10 для получения процента от 0 до 100

        playlist.progress_percent = percent
        playlist.progress_known = result_count
        playlist.progress_total = total_words
        hue = int(120 * (percent / 100)) if percent else 0
        playlist.progress_color = f"hsl({hue}, 70%, 45%)"

        # Последняя дата повторения
        last_game = GameResult.objects.filter(user=request.user, playlist=playlist).order_by('-created_at').first()
        if last_game:
            playlist.last_repeat = timesince(last_game.created_at, now()) + " назад"
        else:
            playlist.last_repeat = "Нет данных"

    return render(request, 'playlist/playlist_list.html', {

        'playlists': playlists,
        'color_filter': color_filter,
        'color_choices': Playlist.COLOR_CHOICES,
        'language': language,
    })

@login_required
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            return redirect('playlist_list')  # например
    else:
        form = PlaylistForm()
    return render(request, 'playlist/create_playlist.html', {'form': form})

@login_required
def create_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('playlist_list')  # или другая страница
    else:
        form = WordForm(user=request.user)
    return render(request, 'playlist/create_word.html', {'form': form})

@login_required
def edit_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            return redirect('playlist_list')
    else:
        form = PlaylistForm(instance=playlist)
    return render(request, 'playlist/edit_playlist.html', {'form': form})

@login_required
def delete_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)
    if request.method == 'POST':
        playlist.delete()
        return redirect('playlist_list')
    return render(request, 'playlist/delete_playlist.html', {'playlist': playlist})

@login_required
def edit_word(request, pk):
    word = get_object_or_404(Word, pk=pk)
    if request.method == 'POST':
        form = WordForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            return redirect('playlist_list')
    else:
        form = WordForm(instance=word)
    return render(request, 'playlist/edit_word.html', {'form': form})

@login_required
def delete_word(request, pk):
    word = get_object_or_404(Word, pk=pk)
    if request.method == 'POST':
        word.delete()
        return redirect('playlist_list')
    return render(request, 'playlist/delete_word.html', {'word': word})

@login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    words = playlist.words.all()
    user = request.user

    # --- Упрощённый расчёт прогресса ---
    word_stats = []
    total_current = 0

    for word in words:
        result = WordResult.objects.filter(user=user, word=word).first()
        current = result.current_result if result and result.current_result is not None else 0

        percent_known = current * 10  # current_result от 0 до 10

        word_stats.append({
            'word': word,
            'known': result.known_count if result else 0,
            'unknown': result.unknown_count if result else 0,
            'percent_known': percent_known,
        })

        total_current += current

    if words.exists():
        max_total = len(words) * 10
        playlist_progress = round((total_current / max_total) * 100)
    else:
        playlist_progress = None

    # Форма добавления слова
    if request.method == 'POST':
        form = WordForm(request.POST, user=request.user)
        if form.is_valid():
            word = form.save(commit=False)
            word.playlists = playlist
            word.save()
            return redirect('playlist_detail', pk=playlist.pk)
    else:
        form = WordForm(user=request.user)

    # Данные для графика (оставляем как есть)
    stats = (GameResult.objects
             .filter(user=user, playlist=playlist)
             .annotate(date=TruncDate('created_at'))
             .values('date')
             .annotate(games_count=Count('id'),
                       known_sum=Sum('known'),
                       unknown_sum=Sum('unknown'))
             .order_by('date'))

    chart_data = []
    for item in stats:
        chart_data.append({
            'date': item['date'].strftime('%Y-%m-%d'),
            'games_count': item['games_count'],
            'known_sum': item['known_sum'],
            'unknown_sum': item['unknown_sum'],
        })

    return render(request, 'playlist/playlist_detail.html', {
        'playlist': playlist,
        'word_stats': word_stats,
        'playlist_progress': playlist_progress,
        'form': form,
        'chart_data': chart_data,
    })


@login_required
def remove_word_from_playlist(request, playlist_pk, word_pk):
    playlist = get_object_or_404(Playlist, pk=playlist_pk)
    word = get_object_or_404(Word, pk=word_pk)
    if word.playlists == playlist:
        word.delete()
    return redirect('playlist_detail', pk=playlist.pk)

@login_required
def bulk_upload_words(request):
    if request.method == 'POST':
        form = WordBulkUploadForm(request.POST, user=request.user)  # передаём user в форму
        if form.is_valid():
            playlist = form.cleaned_data['playlist']
            json_data = form.cleaned_data['json_data']

            try:
                word_list = json.loads(json_data)

                # Проверка: это должен быть массив
                if not isinstance(word_list, list):
                    form.add_error('json_data', 'Ожидался JSON-массив объектов.')
                    return render(request, 'playlist/bulk_upload.html', {'form': form})

                count = 0
                for i, item in enumerate(word_list, start=1):
                    # Проверка: каждый элемент — словарь
                    if not isinstance(item, dict):
                        form.add_error('json_data', f'Элемент №{i} не является объектом.')
                        return render(request, 'playlist/bulk_upload.html', {'form': form})

                    word = item.get('word')
                    translation = item.get('translation')

                    if not word or not isinstance(word, str):
                        form.add_error('json_data', f'Элемент №{i}: отсутствует или неверен ключ "word".')
                        return render(request, 'playlist/bulk_upload.html', {'form': form})

                    if not translation or not isinstance(translation, str):
                        form.add_error('json_data', f'Элемент №{i}: отсутствует или неверен ключ "translation".')
                        return render(request, 'playlist/bulk_upload.html', {'form': form})

                    details = item.get('details', '')
                    context = item.get('context', '')

                    # Убедимся, что дополнительные поля тоже строки
                    if details and not isinstance(details, str):
                        details = ''
                    if context and not isinstance(context, str):
                        context = ''

                    # Создание слова
                    Word.objects.create(
                        word=word.strip(),
                        translation=translation.strip(),
                        details=details.strip(),
                        context=context.strip(),
                        playlists=playlist
                    )
                    count += 1

                messages.success(request, f"Успешно добавлено {count} слов в плейлист «{playlist.title}».")
                return redirect('playlist_detail', playlist.id)

            except json.JSONDecodeError:
                form.add_error('json_data', 'Некорректный JSON. Убедитесь, что вы вставили правильный формат.')

    else:

        form = WordBulkUploadForm(user=request.user)  # при GET тоже передаём user

    return render(request, 'playlist/bulk_upload.html', {'form': form})

@login_required
def favorites_list(request):
    words_list = FavoriteWord.objects.filter(user=request.user)
    return render(request, 'playlist/favorites_list.html', {'list': words_list})

@login_required
def add_word_to_favorites(request, word_pk):
    if request.method == 'POST':
        word = get_object_or_404(Word, pk=word_pk)
        favorite, created = FavoriteWord.objects.get_or_create(user=request.user, word=word)
        if not created:
            # Если слово уже в избранном, можно его удалить (toggle)
            favorite.delete()
            return JsonResponse({'success': True, 'added': False})
        return JsonResponse({'success': True, 'added': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

