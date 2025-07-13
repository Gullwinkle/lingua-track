import os
from gtts import gTTS
from django.core.files.base import ContentFile
from tts.models import AudioCache
from django.conf import settings
from django.utils import timezone

class TTSService:
    def generate_audio(self, word, user, language='en'):
        """
        Генерирует аудиофайл для слова и сохраняет его в кэше.
        Args:
            word (str): Слово для озвучивания.
            user (User): Пользователь, для которого создаётся аудио.
            language (str): Код языка (например, 'en', 'ru').
        Returns:
            AudioCache: Объект кэша с аудиофайлом.
        """
        # Проверка кэша
        cache, created = AudioCache.objects.get_or_create(
            word=word,
            user=user,
            language=language,
            defaults={'audio_file': ''}
        )

        if created or not cache.audio_file:
            # Генерация аудио
            tts = gTTS(text=word, lang=language, slow=False)
            file_name = f"{user.id}_{word}_{language}.mp3"
            file_path = os.path.join(settings.MEDIA_ROOT, 'audio', str(timezone.now().year), str(timezone.now().month),
                                     str(timezone.now().day), file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Сохранение аудиофайла
            tts.save(file_path)
            with open(file_path, 'rb') as f:
                cache.audio_file.save(file_name, ContentFile(f.read()))
            cache.save()

        return cache