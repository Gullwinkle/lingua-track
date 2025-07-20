from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

class Schedule(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    next_review = models.DateField(default=timezone.now)
    interval = models.IntegerField(default=1)  # дни до следующего повтора
    repetition = models.IntegerField(default=0)  # номер повтора
    efactor = models.FloatField(default=2.5)  # easiness factor
    last_quality = models.IntegerField(default=0)  # оценка от 0 до 5

    def __str__(self):
        return f"{self.card.word} — next: {self.next_review}"