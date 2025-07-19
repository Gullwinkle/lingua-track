# cards/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Card, ReviewSchedule
from .forms import CardForm
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
            ReviewSchedule.objects.create(card=card)  # Создаем расписание для новой карточки
            return redirect('card_list')
    else:
        form = CardForm()
    return render(request, 'cards/card_add.html', {'form': form})

@login_required
def review_today(request):
    today = date.today()
    due_schedules = ReviewSchedule.objects.filter(card__user=request.user, next_review__lte=today)
    return render(request, 'cards/review_today.html', {'schedules': due_schedules})

@login_required
def review_result(request, schedule_id, quality):
    schedule = get_object_or_404(ReviewSchedule, id=schedule_id, card__user=request.user)
    quality = int(quality)
    schedule.update_schedule(quality)
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
