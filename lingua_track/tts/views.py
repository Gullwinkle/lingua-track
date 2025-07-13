from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tts.services import TTSService
from tts.serializers import AudioCacheSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse
import os


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


@login_required
def say_word_file(request, word):
    """
    Возвращает аудиофайл напрямую для использования в <audio>.
    """
    tts_service = TTSService()
    audio_cache = tts_service.generate_audio(word=word, user=request.user, language='en')
    file_path = audio_cache.audio_file.path
    return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')