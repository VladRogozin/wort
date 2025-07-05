from django.db import models
from django.contrib.auth.models import User
from playlist.models import Playlist, Word

class GameResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_results')
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='game_results')
    known = models.PositiveIntegerField()
    unknown = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.playlist.title} — {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class WordResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    known_count = models.PositiveIntegerField(default=0)
    unknown_count = models.PositiveIntegerField(default=0)
    current_result = models.IntegerField(default=0, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'word')