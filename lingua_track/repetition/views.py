from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Schedule
from .algorithms import update_schedule, get_due_cards
from core.models import Card, Stats
from django.utils import timezone
import random


@login_required
def review_list(request):
    schedules = get_due_cards(request.user)
    return render(request, 'repetition/review_session.html', {'schedules': schedules})


@login_required
def review_card(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    card = schedule.card
    if request.method == 'POST':
        quality = int(request.POST.get('quality', 0))
        update_schedule(schedule, quality)

        # Обновление статистики
        stats, created = Stats.objects.get_or_create(user=request.user, card=card)
        if quality >= 3:
            stats.correct_answers += 1
        else:
            stats.incorrect_answers += 1
        stats.total_reviews += 1
        stats.last_reviewed = timezone.now()
        stats.save()

        messages.success(request, f"Карточка '{card.word}' обновлена!")
        return redirect('repetition:review_list')

    return render(request, 'repetition/review_card.html', {'schedule': schedule, 'card': card})


@login_required
def test_multiple_choice(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    card = schedule.card

    # Выбор случайных вариантов ответа
    other_cards = Card.objects.filter(user=request.user).exclude(id=card.id)
    choices = random.sample(list(other_cards), min(3, other_cards.count())) + [card]
    random.shuffle(choices)

    if request.method == 'POST':
        selected_translation = request.POST.get('translation')
        quality = 5 if selected_translation == card.translation else 0
        update_schedule(schedule, quality)

        # Обновление статистики
        stats, created = Stats.objects.get_or_create(user=request.user, card=card)
        if quality >= 3:
            stats.correct_answers += 1
        else:
            stats.incorrect_answers += 1
        stats.total_reviews += 1
        stats.last_reviewed = timezone.now()
        stats.save()

        messages.success(request, f"Карточка '{card.word}' протестирована!")
        return redirect('repetition:review_list')

    return render(
        request,
        'repetition/test_mode.html',
        {'schedule': schedule, 'card': card, 'choices': choices}
    )