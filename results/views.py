# results/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from .models import GameResult
from playlist.models import Playlist

from django.utils import timezone

@csrf_exempt
@login_required
def save_game_result(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            playlist_id = data.get('playlist_id')
            known = data.get('known')
            unknown = data.get('unknown')

            playlist = Playlist.objects.get(id=playlist_id, user=request.user)

            # Сохраняем результат
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



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import WordResult
from playlist.models import Word  # если слова в отдельном приложении

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
                result, created = WordResult.objects.get_or_create(user=request.user, word=word)

                if is_known:
                    result.known_count += 1
                else:
                    result.unknown_count += 1

                result.save()

            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
