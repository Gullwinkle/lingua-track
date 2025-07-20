from django.contrib import admin
from .models import Card, Schedule

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['word', 'translation', 'level', 'language', 'user']
    search_fields = ['word', 'translation']

@admin.register(Schedule)
class ReviewScheduleAdmin(admin.ModelAdmin):
    list_display = ['card', 'next_review', 'interval', 'repetition', 'efactor']

