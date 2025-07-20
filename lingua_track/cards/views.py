# cards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Card, Schedule
from .forms import CardForm
from .utils import update_schedule
from datetime import date



@login_required
def card_list(request):
    cards = Card.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cards/card_list.html', {'cards': cards})

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
