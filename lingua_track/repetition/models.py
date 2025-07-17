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
   interval = models.PositiveIntegerField(default=1)
   easiness = models.FloatField(default=2.5)
   repetitions = models.PositiveIntegerField(default=0)
   is_active = models.BooleanField(default=True)

   class Meta:
       unique_together = ('user', 'card')

   def __str__(self):
       return f"Schedule for {self.card.word} (User: {self.user.username})"

class Review(models.Model):
   card = models.ForeignKey(Card, on_delete=models.CASCADE)
   review_date = models.DateTimeField(auto_now_add=True)
   success = models.BooleanField(default=False)

   def __str__(self):
       return f"Review for {self.card.word} - {'Success' if self.success else 'Failure'}"

class TestSession(models.Model):
   telegram_id = models.CharField(max_length=100, unique=True)
   card = models.ForeignKey(Card, on_delete=models.CASCADE)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
       return f"TestSession for {self.telegram_id} - Card: {self.card.word}"