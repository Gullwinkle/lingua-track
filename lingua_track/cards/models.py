from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

LEVEL_CHOICES = [
    ('beginner', 'Начальный'),
    ('intermediate', 'Средний'),
    ('advanced', 'Продвинутый'),
]

LANGUAGE_CHOICES = [
    ('en', 'Английский'),
    ('de', 'Немецкий'),
    ('es', 'Испанский'),
]

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)
    example = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.word} - {self.translation}"

class ReviewSchedule(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE)
    next_review = models.DateField(default=timezone.now)
    interval = models.IntegerField(default=1)
    repetitions = models.IntegerField(default=0)
    ease_factor = models.FloatField(default=2.5)

    def update_schedule(self, quality):
        if quality >= 3:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            self.repetitions += 1
        else:
            self.repetitions = 0
            self.interval = 1

        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        self.next_review = timezone.now().date() + timedelta(days=self.interval)
        self.save()

class TTSCache(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='tts_audio/')
    created_at = models.DateTimeField(auto_now_add=True)
