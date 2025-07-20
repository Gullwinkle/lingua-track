# users/views.py
from collections import defaultdict
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from cards.models import Card, Schedule
from datetime import date

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "users/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard_view(request):
    user = request.user
    tg_link = f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={user.userprofile.telegram_token}"

    total_cards = Card.objects.filter(user=user).count()
    due_cards = Schedule.objects.filter(user=user, next_review__lte=date.today()).count()
    learned_cards = total_cards - due_cards
    percent_learned = int((learned_cards / total_cards) * 100) if total_cards else 0

    quality_stats = defaultdict(int)
    for sched in Schedule.objects.filter(user=user):
        quality_stats[sched.last_quality] += 1

    upcoming_reviews = Schedule.objects.filter(user=user, next_review__gt=date.today()).order_by('next_review')[:5]

    return render(request, "users/dashboard.html", {
        "tg_link": tg_link,
        "total_cards": total_cards,
        "due_cards": due_cards,
        "learned_cards": learned_cards,
        "percent_learned": percent_learned,
        "quality_stats": dict(sorted(quality_stats.items())),
        "upcoming_reviews": upcoming_reviews,
    })
