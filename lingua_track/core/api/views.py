from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from core.models import TelegramLink, Card
from repetition.models import Schedule, Review, TestSession
from django.utils import timezone
from tts.services import TTSService
from tts.serializers import AudioCacheSerializer
import random

@api_view(['GET'])
def today(request):
   telegram_id = request.query_params.get('telegram_id')
   try:
       user = TelegramLink.objects.get(telegram_id=telegram_id).user
       schedules = Schedule.objects.filter(user=user, next_review__lte=timezone.now(), is_active=True).select_related('card')
       cards = [{'word': s.card.word, 'translation': s.card.translation} for s in schedules]
       return Response(cards)
   except TelegramLink.DoesNotExist:
       return Response({'error': 'Пользователь не найден'}, status=404)

@api_view(['GET'])
def cards(request):
   telegram_id = request.query_params.get('telegram_id')
   try:
       user = TelegramLink.objects.get(telegram_id=telegram_id).user
       cards = Card.objects.filter(user=user)
       data = [{'word': card.word, 'translation': card.translation} for card in cards]
       return Response(data)
   except TelegramLink.DoesNotExist:
       return Response({'error': 'Пользователь не найден'}, status=404)

@api_view(['GET'])
def progress(request):
   telegram_id = request.query_params.get('telegram_id')
   try:
       user = TelegramLink.objects.get(telegram_id=telegram_id).user
       total_cards = Card.objects.filter(user=user).count()
       learned_cards = Schedule.objects.filter(user=user, is_active=False).count()
       total_reviews = Review.objects.filter(card__user=user).count()
       return Response({
           'total_cards': total_cards,
           'learned_cards': learned_cards,
           'total_reviews': total_reviews
       })
   except TelegramLink.DoesNotExist:
       return Response({'error': 'Пользователь не найден'}, status=404)

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
       return Response({'error': 'Пользователь не найден'}, status=404)

@api_view(['GET'])
def test(request):
   telegram_id = request.query_params.get('telegram_id')
   try:
       user = TelegramLink.objects.get(telegram_id=telegram_id).user
       schedules = Schedule.objects.filter(user=user, is_active=True)
       if not schedules:
           return Response({'error': 'У вас нет карточек для теста.'})
       schedule = random.choice(schedules)
       card = schedule.card
       choices = [{'translation': card.translation, 'correct': True}]
       other_cards = Card.objects.filter(user=user).exclude(id=card.id)[:3]
       choices.extend([{'translation': c.translation, 'correct': False} for c in other_cards])
       random.shuffle(choices)
       # Сохраняем card_id в TestSession
       TestSession.objects.update_or_create(
           telegram_id=telegram_id,
           defaults={'card': card}
       )
       return Response({
           'card': {'word': card.word, 'translation': card.translation},
           'choices': choices
       })
   except TelegramLink.DoesNotExist:
       return Response({'error': 'Пользователь не найден'}, status=404)

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def test_submit(request):
   telegram_id = request.data.get('telegram_id')
   answer = request.data.get('answer')
   if not telegram_id or not answer:
       return Response({'error': 'Не указаны telegram_id или answer'}, status=400)
   try:
       user = TelegramLink.objects.get(telegram_id=telegram_id).user
       test_session = TestSession.objects.filter(telegram_id=telegram_id).first()
       if not test_session:
           return Response({'error': 'Тест не начат.'}, status=400)
       card = test_session.card
       schedule = Schedule.objects.get(card=card, user=user)
       correct = answer == card.translation
       Review.objects.create(card=card, success=correct)
       if correct:
           schedule.repetitions += 1
           schedule.easiness = max(1.3, schedule.easiness + 0.1 - 0.8 * (5 - 4) / 17)
           schedule.interval = max(1, schedule.interval * schedule.easiness)
           schedule.next_review = timezone.now() + timezone.timedelta(days=schedule.interval)
       else:
           schedule.repetitions = 0
           schedule.interval = 1
           schedule.next_review = timezone.now()
       schedule.last_reviewed = timezone.now()
       schedule.save()
       # Удаляем TestSession после ответа
       test_session.delete()
       return Response({
           'correct': correct,
           'correct_translation': card.translation
       })
   except TelegramLink.DoesNotExist:
       return Response({'error': 'Пользователь не найден'}, status=404)
   except Card.DoesNotExist:
       return Response({'error': 'Карточка не найдена'}, status=404)
   except Schedule.DoesNotExist:
       return Response({'error': 'Расписание не найдено'}, status=404)
   except Exception as e:
       return Response({'error': str(e)}, status=400)