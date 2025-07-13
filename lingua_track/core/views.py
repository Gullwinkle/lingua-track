from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from core.models import Card, TelegramLink
from core.forms import CardForm, TelegramLinkForm, UserRegisterForm
from django.contrib.auth import login
from django.db.models import Count
from repetition.models import Schedule


@login_required
def card_list(request):
    cards = Card.objects.filter(user=request.user).annotate(
        next_review=Schedule.objects.filter(card_id=models.OuterRef('pk')).values('next_review')[:1]
    )
    return render(request, 'core/card_list.html', {'cards': cards})


@login_required
def card_detail(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    return render(request, 'core/card_detail.html', {'card': card})


@login_required
def card_create(request):
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            Schedule.objects.create(user=request.user, card=card)
            messages.success(request, f"Карточка '{card.word}' создана!")
            return redirect('core:card_list')
    else:
        form = CardForm()
    return render(request, 'core/card_form.html', {'form': form, 'title': 'Добавить карточку'})


@login_required
def card_edit(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, f"Карточка '{card.word}' обновлена!")
            return redirect('core:card_list')
    else:
        form = CardForm(instance=card)
    return render(request, 'core/card_form.html', {'form': form, 'title': 'Редактировать карточку'})


@login_required
def card_delete(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    if request.method == 'POST':
        card.delete()
        messages.success(request, f"Карточка '{card.word}' удалена!")
        return redirect('core:card_list')
    return render(request, 'core/card_confirm_delete.html', {'card': card})


@login_required
def progress(request):
    total_cards = Card.objects.filter(user=request.user).count()
    learned_cards = Card.objects.filter(user=request.user, stats__correct_answers__gte=3).count()
    total_reviews = Schedule.objects.filter(user=request.user).aggregate(total_reviews=Count('id'))['total_reviews']
    stats = Card.objects.filter(user=request.user, stats__total_reviews__gt=0)
    context = {
        'total_cards': total_cards,
        'learned_cards': learned_cards,
        'total_reviews': total_reviews or 0,
        'stats': stats
    }
    return render(request, 'core/progress.html', {'context': context})


@login_required
def telegram_link(request):
    telegram_link, created = TelegramLink.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = TelegramLinkForm(request.POST, instance=telegram_link)
        if form.is_valid():
            form.save()
            messages.success(request, 'Telegram ID успешно сохранён!')
            return redirect('core:progress')
    else:
        form = TelegramLinkForm(instance=telegram_link)
    return render(request, 'core/telegram_link.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            messages.success(request, f'Аккаунт для {user.username} создан! Вы вошли в систему.')
            return redirect('core:card_list')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})