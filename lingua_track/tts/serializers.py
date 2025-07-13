from rest_framework import serializers
from tts.models import AudioCache


class AudioCacheSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = AudioCache
        fields = ['word', 'language', 'audio_url']
        read_only_fields = ['word', 'language', 'audio_url']

    def get_audio_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.audio_file.url)