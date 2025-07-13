from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Card(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cards'
    )
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    example = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default='beginner'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    interval = models.PositiveIntegerField(default=1)  # Интервал повторения в днях
    easiness = models.FloatField(default=2.5)  # Фактор лёгкости для SM-2
    repetitions = models.PositiveIntegerField(default=0)  # Количество повторений

    def __str__(self):
        return f"{self.word} ({self.translation})"


class Stats(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='stats'
    )
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name='stats', null=True
    )
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.user.username} - {self.card.word if self.card else 'General'}"


class TelegramLink(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='telegram_link'
    )
    telegram_id = models.CharField(max_length=50, unique=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Telegram ID: {self.telegram_id}"


class BotLog(models.Model):
    telegram_id = models.CharField(max_length=50)
    command = models.CharField(max_length=100)
    response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Log: {self.command} at {self.timestamp}"