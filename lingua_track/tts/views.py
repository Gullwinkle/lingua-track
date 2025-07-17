from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
from tts.services import TTSService
from tts.serializers import AudioCacheSerializer
from core.models import TelegramLink
import logging
import os

logger = logging.getLogger(__name__)

@login_required
def say_word(request, word):
    """
    Генерирует и возвращает аудиофайл для слова через веб-интерфейс.
    """
    tts_service = TTSService()
    audio_cache = tts_service.generate_audio(word=word, user=request.user, language='en')
    audio_url = request.build_absolute_uri(audio_cache.audio_file.url)
    return render(request, 'tts/say_word.html', {'word': word, 'audio_url': audio_url})

@api_view(['GET'])
@login_required
def say_word_api(request, word):
    """
    Возвращает JSON с URL аудиофайла для слова (для API и Telegram-бота).
    """
    tts_service = TTSService()
    audio_cache = tts_service.generate_audio(word=word, user=request.user, language='en')
    serializer = AudioCacheSerializer(audio_cache, context={'request': request})
    return Response(serializer.data)

def say_word_file(request, word):
    """
    Возвращает аудиофайл напрямую для использования в Telegram или <audio>.
    """
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        logger.error('Отсутствует telegram_id в запросе')
        return Response({'error': 'Не указан telegram_id'}, status=400)
    try:
        user = TelegramLink.objects.get(telegram_id=telegram_id).user
        tts_service = TTSService()
        audio_cache = tts_service.generate_audio(word=word, user=user, language='en')
        file_path = audio_cache.audio_file.path
        logger.info(f'Возвращён аудиофайл для слова "{word}": {file_path}')
        return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
    except TelegramLink.DoesNotExist:
        logger.error(f'Пользователь с telegram_id {telegram_id} не найден')
        return Response({'error': 'Пользователь не найден'}, status=404)
    except Exception as e:
        logger.error(f'Ошибка в say_word_file для слова "{word}": {str(e)}')
        return Response({'error': str(e)}, status=500)