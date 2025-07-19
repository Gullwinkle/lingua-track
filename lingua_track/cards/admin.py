from django.contrib import admin
from .models import Card, ReviewSchedule, TTSCache

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['word', 'translation', 'level', 'language', 'user']
    search_fields = ['word', 'translation']

@admin.register(ReviewSchedule)
class ReviewScheduleAdmin(admin.ModelAdmin):
    list_display = ['card', 'next_review', 'interval', 'repetitions', 'ease_factor']

@admin.register(TTSCache)
class TTSCacheAdmin(admin.ModelAdmin):
    list_display = ['card', 'audio_file', 'created_at']
