from django.db import models
from django.contrib.auth.models import User
from cards.models import Card

class ReviewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    result = models.BooleanField()
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.card.word} - {'✔️' if self.result else '❌'}"
