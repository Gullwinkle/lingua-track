# api/views.py
import io
import random
from django.http import HttpResponse
from gtts import gTTS
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from cards.models import Card, Schedule
from users.models import UserProfile
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
        schedules = Schedule.objects.filter(card__user=profile.user, next_review__lte=today)
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
        due = Schedule.objects.filter(card__user=profile.user, next_review__lte=date.today()).count()
        return Response({'total': total, 'due': due})
    except UserProfile.DoesNotExist:
        return Response({'error': 'not registered'}, status=404)

@api_view(['GET'])
def say_word(request, word):
    try:
        tts = gTTS(text=word, lang='en')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return HttpResponse(mp3_fp.read(), content_type="audio/mpeg")
    except Exception:
        return HttpResponse("Ошибка при озвучке", status=500)

@api_view(['GET'])
def test_question(request, telegram_id):
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    cards = list(Card.objects.filter(user=user))
    if len(cards) < 4:
        return Response({"detail": "Недостаточно карточек для теста"}, status=status.HTTP_400_BAD_REQUEST)

    correct = random.choice(cards)

    # Получаем 3 случайных карточки, исключая правильную
    distractors = random.sample([c for c in cards if c.id != correct.id], 3)

    # Формируем список вариантов: правильный + 3 неправильных
    options = [{"id": correct.id, "translation": correct.translation}]
    options += [{"id": d.id, "translation": d.translation} for d in distractors]
    random.shuffle(options)

    data = {
        "word": correct.word,
        "question_id": correct.id,
        "options": options
    }
    return Response(data)
