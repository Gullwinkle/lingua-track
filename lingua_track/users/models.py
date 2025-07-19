from django.contrib.auth.models import User
from django.db import models
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)

    def __str__(self):
        return self.user.username
