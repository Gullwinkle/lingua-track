from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Card, TelegramLink, Stats
from repetition.models import Schedule
from repetition.algorithms import update_schedule
from core.api.serializers import CardSerializer, StatsSerializer
from tts.services import TTSService
from tts.serializers import AudioCacheSerializer
from django.utils import timezone
import random


@api_view(['GET'])
def today_words(request):
    telegram_id = request.query_params.get('telegram_id')
    try:
        user = TelegramLink.objects.get(telegram_id=telegram_id).user
        schedules = Schedule.objects.filter(
            user=user,
            is_active=True,
            next_review__lte=timezone.now()
        ).select_related('card')
        serializer = CardSerializer([s.card for s in schedules], many=True)
        return Response(serializer.data)
    except TelegramLink.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)


@api_view(['GET'])
def user_cards(request):
    telegram_id = request.query_params.get('telegram_id')
    try:
        user = TelegramLink.objects.get(telegram_id=telegram_id).user
        cards = Card.objects.filter(user=user)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)
    except TelegramLink.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)


@api_view(['GET'])
def progress(request):
    telegram_id = request.query_params.get('telegram_id')
    try:
        user = TelegramLink.objects.get(telegram_id=telegram_id).user
        total_cards = Card.objects.filter(user=user).count()
        learned_cards = Stats.objects.filter(user=user, correct_answers__gte=3).count()
        total_reviews = sum(s.total_reviews for s in Stats.objects.filter(user=user))
        return Response({
            'total_cards': total_cards,
            'learned_cards': learned_cards,
            'total_reviews': total_reviews
        })
    except TelegramLink.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)


@api_view(['GET'])
def say_word(request, word):
    telegram_id = request.query_params.get('telegram_id')
    try:
        user = TelegramLink.objects.get(telegram_id=telegram_id).user
        tts_service = TTSService()
        audio_cache = tts_service.generate_audio(word=word, user=user, language='en')
        serializer = AudioCacheSerializer(audio_cache, context={'request': request})
        return Response(serializer.data)
    except TelegramLink.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)


@api_view(['GET'])
def test_card(request):
    telegram_id = request.query_params.get('telegram_id')
    try:
        user = TelegramLink.objects.get(telegram_id=telegram_id).user
        schedules = Schedule.objects.filter(
            user=user,
            is_active=True,
            next_review__lte=timezone.now()
        ).select_related('card')
        if not schedules:
            return Response({"error": "Нет карточек для теста"}, status=404)

        schedule = random.choice(list(schedules))
        card = schedule.card
        other_cards = Card.objects.filter(user=user).exclude(id=card.id)
        choices = random.sample(list(other_cards), min(3, other_cards.count())) + [card]
        random.shuffle(choices)

        return Response({
            "card": CardSerializer(card).data,
            "choices": [{"translation": c.translation, "id": c.id} for c in choices],
            "schedule_id": schedule.id
        })
    except TelegramLink.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)


@api_view(['POST'])
def submit_test_answer(request):
    telegram_id = request.data.get('telegram_id')
    answer = request.data.get('answer')
    try:
        user = TelegramLink.objects.get(telegram_id=telegram_id).user
        schedules = Schedule.objects.filter(
            user=user,
            is_active=True,
            next_review__lte=timezone.now()
        ).select_related('card')
        if not schedules:
            return Response({"error": "Нет активных тестов"}, status=404)

        schedule = random.choice(list(schedules))
        card = schedule.card
        correct = answer == card.translation
        quality = 5 if correct else 0
        update_schedule(schedule, quality)

        stats, _ = Stats.objects.get_or_create(user=user, card=card)
        stats.correct_answers += 1 if correct else 0
        stats.incorrect_answers += 1 if not correct else 0
        stats.total_reviews += 1
        stats.last_reviewed = timezone.now()
        stats.save()

        return Response({
            "correct": correct,
            "correct_translation": card.translation
        })
    except TelegramLink.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=404)