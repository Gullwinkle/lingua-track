# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from cards.models import Card, ReviewSchedule
from users.models import UserProfile
from django.contrib.auth.models import User
from datetime import date

@api_view(['POST'])
def link_telegram(request):
    telegram_id = request.data.get("telegram_id")
    token = request.data.get("token")

    if not telegram_id or not token:
        return Response({"error": "Missing data"}, status=400)

    try:
        profile = UserProfile.objects.get(telegram_token=token)
        profile.telegram_id = telegram_id
        profile.save()
        return Response({"status": "linked"})
    except UserProfile.DoesNotExist:
        return Response({"error": "Invalid token"}, status=404)


@api_view(['GET'])
def get_today_cards(request, telegram_id):
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        today = date.today()
        schedules = ReviewSchedule.objects.filter(card__user=profile.user, next_review__lte=today)
        result = [
            {'word': s.card.word, 'translation': s.card.translation}
            for s in schedules
        ]
        return Response(result)
    except UserProfile.DoesNotExist:
        return Response({'error': 'not registered'}, status=404)

@api_view(['GET'])
def get_progress(request, telegram_id):
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        total = Card.objects.filter(user=profile.user).count()
        due = ReviewSchedule.objects.filter(card__user=profile.user, next_review__lte=date.today()).count()
        return Response({'total': total, 'due': due})
    except UserProfile.DoesNotExist:
        return Response({'error': 'not registered'}, status=404)
