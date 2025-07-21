from celery import shared_task
from django.utils import timezone
from .models import Schedule
from telegram_bot.utils import send_telegram_message  # ты можешь создать этот хелпер

@shared_task
def send_review_reminders():
    today = timezone.now().date()
    schedules = Schedule.objects.filter(next_review=today)

    count = 0
    for sched in schedules:
        tg_id = sched.user.userprofile.telegram_id
        if tg_id:
            message = f"👋 Сегодня нужно повторить слово: {sched.card.word}"
            send_telegram_message(tg_id, message)
            count += 1

    return f"Напоминания отправлены: {count}"
