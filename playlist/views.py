from django.shortcuts import render, redirect
from .forms import PlaylistForm, WordForm
from .models import Playlist
from django.contrib.auth.decorators import login_required

from results.models import GameResult


@login_required
def playlist_list(request):
    color_filter = request.GET.get('color')
    playlists = Playlist.objects.filter(user=request.user)
    if color_filter:
        playlists = playlists.filter(color=color_filter)
    return render(request, 'playlist/playlist_list.html', {
        'playlists': playlists,
        'color_filter': color_filter,
        'color_choices': Playlist.COLOR_CHOICES,
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


from .forms import WordForm
from results.models import WordResult


from django.db.models.functions import TruncDate
from django.db.models import Count, Sum

@login_required
def playlist_detail(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk, user=request.user)
    words = playlist.words.all()
    user = request.user

    # --- Статистика слов (ваш существующий код) ---
    if not words.exists():
        playlist_progress = None  # Прогресс не вычисляется
        word_stats = []
    else:
        # Собираем статистику по каждому слову
        word_stats = []
        total_total = 0
        total_known = 0

        for word in words:
            result = WordResult.objects.filter(user=user, word=word).first()
            known = result.known_count if result else 0
            unknown = result.unknown_count if result else 0
            total = 100 if ((known - unknown) * 10) >= 100 else ((known - unknown) * 10)

            percent_known = total if total > 0 else 0

            word_stats.append({
                'word': word,
                'known': known,
                'unknown': unknown,
                'percent_known': percent_known,
            })

            if total > 0:
                total_known += known - unknown

            total_total += 1

        if total_total > 0:
            playlist_progress = 100 if (total_known / total_total * 10) >= 100 else round(total_known / total_total * 10)
        else:
            playlist_progress = 0

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
    stats = (GameResult.objects
             .filter(user=user, playlist=playlist)
             .annotate(date=TruncDate('created_at'))
             .values('date')
             .annotate(games_count=Count('id'),
                       known_sum=Sum('known'),
                       unknown_sum=Sum('unknown'))
             .order_by('date'))

    # Преобразуем QuerySet в список словарей с датой и значениями
    chart_data = []
    for item in stats:
        chart_data.append({
            'date': item['date'].strftime('%Y-%m-%d'),
            'games_count': item['games_count'],
            'known_sum': item['known_sum'],
            'unknown_sum': item['unknown_sum'],
        })

    # Форма добавления слова (ваш код)
    if request.method == 'POST':
        form = WordForm(request.POST, user=request.user)
        if form.is_valid():
            word = form.save(commit=False)
            word.playlists = playlist
            word.save()
            return redirect('playlist_detail', pk=playlist.pk)
    else:
        form = WordForm(user=request.user)

    stats = (GameResult.objects
             .filter(user=user, playlist=playlist)
             .annotate(date=TruncDate('created_at'))
             .values('date')
             .annotate(games_count=Count('id'),
                       known_sum=Sum('known'),
                       unknown_sum=Sum('unknown'))
             .order_by('date'))

    # Преобразуем QuerySet в список словарей с датой и значениями
    chart_data = []
    for item in stats:
        chart_data.append({
            'date': item['date'].strftime('%Y-%m-%d'),
            'games_count': item['games_count'],
            'known_sum': item['known_sum'],
            'unknown_sum': item['unknown_sum'],
        })

    # Форма добавления слова (ваш код)
    if request.method == 'POST':
        form = WordForm(request.POST, user=request.user)
        if form.is_valid():
            word = form.save(commit=False)
            word.playlists = playlist
            word.save()
            return redirect('playlist_detail', pk=playlist.pk)
    else:
        form = WordForm(user=request.user)

    return render(request, 'playlist/playlist_detail.html', {
        'playlist': playlist,
        'word_stats': word_stats,
        'playlist_progress': playlist_progress,
        'form': form,
        'chart_data': chart_data,  # Передаём в шаблон
    })



@login_required
def remove_word_from_playlist(request, playlist_pk, word_pk):
    playlist = get_object_or_404(Playlist, pk=playlist_pk)
    word = get_object_or_404(Word, pk=word_pk)
    if word.playlists == playlist:
        word.delete()
    return redirect('playlist_detail', pk=playlist.pk)


import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import WordBulkUploadForm
from .models import Word, Playlist
from django.contrib.auth.decorators import login_required

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



from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import FavoriteWord, Word

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