from django.db import models
from django.contrib.auth.models import User

class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Word(models.Model):
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=255)
    details = models.TextField(help_text="Подробная информация о слове")
    context = models.TextField(help_text="Слово в контексте")
    playlists = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='words')

    def __str__(self):
        return self.word
