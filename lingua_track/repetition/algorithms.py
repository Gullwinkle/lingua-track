from datetime import timedelta
from django.utils import timezone
from .models import Schedule


def update_schedule(schedule, quality):
    """
    Обновляет расписание повторений карточки на основе алгоритма SM-2.

    Args:
        schedule (Schedule): Объект расписания для карточки.
        quality (int): Качество ответа (0-5, где 0 - полное забывание, 5 - идеальное запоминание).
    """
    # Проверка корректности качества ответа
    if not 0 <= quality <= 5:
        raise ValueError("Качество ответа должно быть от 0 до 5")

    # Обновление фактора лёгкости
    schedule.easiness = max(1.3, schedule.easiness + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Обновление количества повторений
    if quality < 3:
        schedule.repetitions = 0
        schedule.interval = 1
    else:
        schedule.repetitions += 1
        if schedule.repetitions == 1:
            schedule.interval = 1
        elif schedule.repetitions == 2:
            schedule.interval = 6
        else:
            schedule.interval = int(schedule.interval * schedule.easiness)

    # Обновление даты следующего повторения
    schedule.last_reviewed = timezone.now()
    schedule.next_review = timezone.now() + timedelta(days=schedule.interval)

    # Сохранение изменений
    schedule.save()


def get_due_cards(user):
    """
    Возвращает карточки, которые нужно повторить для указанного пользователя.

    Args:
        user: Объект пользователя (User).

    Returns:
        QuerySet: Список карточек, готовых к повторению.
    """
    return Schedule.objects.filter(
        user=user,
        is_active=True,
        next_review__lte=timezone.now()
    ).select_related('card')