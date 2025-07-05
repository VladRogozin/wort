from django.db import models
from django.contrib.auth.models import User


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)


    COLOR_CHOICES = [
        ('#a8a8a8', 'Серый'),
        ('#e57373', 'Красный'),
        ('#ffb74d', 'Оранжевый'),
        ('#fff176', 'Желтый'),
        ('#81c784', 'Зелёный'),
        ('#64b5f6', 'Синий'),
        ('#7986cb', 'Индиго'),
        ('#ba68c8', 'Фиолетовый'),
        ('#f06292', 'Розовый'),
        ('#4dd0e1', 'Бирюзовый'),
        ('#4db6ac', 'Морской волны'),
        ('#dce775', 'Лайм'),
        ('#a1887f', 'Коричневый'),
        ('#ce93d8', 'Сиреневый'),
        ('#90caf9', 'Темно-синий (navy)'),
        ('#c5e1a5', 'Оливковый'),
        ('#ffd54f', 'Золотой'),
        ('#b0bec5', 'Серебристый'),
        ('#eeeeee', 'Светло-серый'),
    ]

    LANGUAGE_CHOICES = [
        ('DE', 'DE'),
        ('EN', 'EN'),
    ]

    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default='black'
    )

    language = models.CharField(
        max_length=3,
        choices=LANGUAGE_CHOICES,
        default='EN'
    )

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


class FavoriteWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_words')
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='favorites')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'word')  # одно слово не может быть добавлено в избранное дважды

    def __str__(self):
        return f"{self.user.username} — {self.word.word}"