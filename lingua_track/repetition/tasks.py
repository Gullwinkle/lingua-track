from celery import shared_task
from django.utils import timezone
from repetition.models import Schedule
from core.models import TelegramLink
import requests
from django.conf import settings


@shared_task
def send_review_reminders():
    """
    Отправляет напоминания в Telegram пользователям, у которых есть карточки для повторения.
    Использует API Telegram-бота для отправки сообщений.
    """
    now = timezone.now()
    schedules = Schedule.objects.filter(
        is_active=True,
        next_review__lte=now
    ).select_related('user', 'card')

    for schedule in schedules:
        telegram_link = TelegramLink.objects.filter(user=schedule.user).first()
        if telegram_link:
            telegram_id = telegram_link.telegram_id
            message = (
                f"Пора повторить карточку!\n"
                f"Слово: {schedule.card.word}\n"
                f"Перевод: {schedule.card.translation}\n"
                f"Используйте /today для списка слов или /test для теста."
            )

            # Отправка сообщения через API Telegram-бота
            try:
                response = requests.post(
                    f"{settings.BOT_API_URL}/sendMessage",
                    json={
                        "chat_id": telegram_id,
                        "text": message
                    }
                )
                if response.status_code != 200:
                    print(f"Ошибка отправки напоминания для Telegram ID {telegram_id}: {response.text}")
            except requests.RequestException as e:
                print(f"Ошибка соединения с ботом для Telegram ID {telegram_id}: {e}")