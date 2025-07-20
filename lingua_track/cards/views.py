# cards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import F
from .models import Card, Schedule
from .forms import CardForm
from .utils import update_schedule
from datetime import date
import random


@login_required
def card_list(request):
    sort_field = request.GET.get('sort', 'created_at')
    sort_dir = request.GET.get('dir', 'desc')
    level_filter = request.GET.get('level')

    # Сборка сортировки
    sort_prefix = '' if sort_dir == 'asc' else '-'
    if sort_field == 'efactor':
        cards = Card.objects.filter(user=request.user).annotate(
            efactor=F('schedule__efactor')
        )
        order_by = f'{sort_prefix}efactor'
    else:
        cards = Card.objects.filter(user=request.user)
        order_by = f'{sort_prefix}created_at'

    if level_filter in ['beginner', 'intermediate', 'advanced']:
        cards = cards.filter(level=level_filter)

    cards = cards.order_by(order_by)

    return render(request, 'cards/card_list.html', {
        'cards': cards,
        'sort_field': sort_field,
        'sort_dir': sort_dir,
        'level_filter': level_filter
    })


@login_required
def card_add(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            Schedule.objects.create(card=card, user=request.user)  # Создаем расписание для новой карточки
            return redirect('card_list')
    else:
        form = CardForm()
    return render(request, 'cards/card_add.html', {'form': form})

@login_required
def review_today(request):
    user = request.user
    schedule_qs = Schedule.objects.filter(user=user, next_review__lte=date.today()).order_by('next_review')

    if not schedule_qs.exists():
        return render(request, "cards/review_done.html")

    current_schedule = schedule_qs.first()
    show_translation = request.method == "POST"  # перевод показываем только после POST

    return render(request, "cards/review_today.html", {
        "schedule": current_schedule,
        "show_translation": show_translation,
    })

@login_required
def review_result(request, schedule_id, quality):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    update_schedule(schedule, int(quality))
    return redirect('review_today')


@login_required
def card_detail(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    return render(request, 'cards/card_detail.html', {'card': card})

@login_required
def card_edit(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect('card_list')
    else:
        form = CardForm(instance=card)
    return render(request, 'cards/card_edit.html', {'form': form})

@login_required
def card_delete(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    if request.method == 'POST':
        card.delete()
        return redirect('card_list')
    return render(request, 'cards/card_confirm_delete.html', {'card': card})

@login_required
def card_test(request):
    user_cards = Card.objects.filter(user=request.user)

    if len(user_cards) < 4:
        return render(request, "cards/test.html", {"error": "Добавьте хотя бы 4 карточки для теста."})

    if request.method == "POST":
        selected_translation = request.POST.get("answer")
        correct_translation = request.session.get("correct_translation")

        is_correct = selected_translation == correct_translation
        context = {
            "is_correct": is_correct,
            "selected_translation": selected_translation,
            "correct_translation": correct_translation
        }
        return render(request, "cards/test_result.html", context)

    # GET — новая задача
    correct_card = random.choice(user_cards)
    distractors = random.sample([c for c in user_cards if c != correct_card], 3)
    options = [correct_card] + distractors
    random.shuffle(options)

    # сохранить правильный ответ в сессии
    request.session["correct_translation"] = correct_card.translation

    context = {
        "word": correct_card.word,
        "options": options,
    }
    return render(request, "cards/test.html", context)