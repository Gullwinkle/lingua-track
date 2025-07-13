from django.db import models
from django.contrib.auth.models import User
from core.models import Card
from django.utils import timezone


class Schedule(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='schedules'
    )
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, related_name='schedules'
    )
    next_review = models.DateTimeField(default=timezone.now)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    interval = models.PositiveIntegerField(default=1)  # Интервал в днях
    easiness = models.FloatField(default=2.5)  # Фактор лёгкости (SM-2)
    repetitions = models.PositiveIntegerField(default=0)  # Количество повторений
    is_active = models.BooleanField(default=True)  # Активность расписания

    class Meta:
        unique_together = ('user', 'card')  # Одна карточка на пользователя

    def __str__(self):
        return f"Schedule for {self.card.word} (User: {self.user.username})"