from django.contrib import admin
from .models import ReviewLog

@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'result', 'reviewed_at']
    list_filter = ['result', 'reviewed_at']
