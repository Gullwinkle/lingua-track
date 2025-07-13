from django.db import models
from django.contrib.auth.models import User


class AudioCache(models.Model):
    word = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_caches')
    audio_file = models.FileField(upload_to='audio/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=10, default='en')  # Код языка, например, 'en', 'ru'

    class Meta:
        unique_together = ('user', 'word', 'language')  # Один аудиофайл на слово и язык для пользователя

    def __str__(self):
        return f"{self.word} ({self.language}) - {self.user.username}"