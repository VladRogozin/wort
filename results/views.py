import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import GameResult, WordResult
from playlist.models import Playlist, Word


# Сохраняет общий результат игры (знаю / не знаю) по плейлисту
@csrf_exempt
@login_required
def save_game_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            playlist_id = data.get('playlist_id')
            known = data.get('known')
            unknown = data.get('unknown')

            # Находим плейлист, принадлежащий текущему пользователю
            playlist = Playlist.objects.get(id=playlist_id, user=request.user)

            # Сохраняем результат игры
            GameResult.objects.create(
                user=request.user,
                playlist=playlist,
                known=known,
                unknown=unknown
            )

            # Обновляем дату последнего повторения
            playlist.last_reviewed_at = timezone.now()
            playlist.save(update_fields=['last_reviewed_at'])

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return HttpResponseBadRequest("Invalid request method")


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SaveWordResultsView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            word_results = data.get("word_results", [])

            for item in word_results:
                word_id = item.get("word_id")
                is_known = item.get("is_known")

                word = Word.objects.get(id=word_id)
                result, _ = WordResult.objects.get_or_create(user=request.user, word=word)

                # Обновляем known_count и unknown_count без ограничений
                if is_known:
                    result.known_count += 1
                else:
                    result.unknown_count += 1

                # Обновляем current_result с ограничением от 0 до 10
                if result.current_result is None:
                    result.current_result = 0

                if is_known:
                    if result.current_result < 10:
                        result.current_result += 1
                else:
                    if result.current_result > 0:
                        result.current_result -= 1

                result.save()

            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
