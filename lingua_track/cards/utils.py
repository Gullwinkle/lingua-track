# cards/utils.py
from datetime import timedelta
from django.utils import timezone

def update_schedule(schedule, quality):
    if quality < 3:
        schedule.repetition = 0
        schedule.interval = 1
    else:
        if schedule.repetition == 0:
            schedule.interval = 1
        elif schedule.repetition == 1:
            schedule.interval = 6
        else:
            schedule.interval = round(schedule.interval * schedule.efactor)

        schedule.repetition += 1

    ef = schedule.efactor
    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    schedule.efactor = max(1.3, ef)

    schedule.next_review = timezone.now().date() + timedelta(days=schedule.interval)
    schedule.last_quality = quality
    schedule.save()
