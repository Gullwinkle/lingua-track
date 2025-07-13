from rest_framework import serializers
from core.models import Card, Stats


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'word', 'translation', 'example', 'notes', 'difficulty']
        read_only_fields = ['id']


class StatsSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)

    class Meta:
        model = Stats
        fields = ['card', 'correct_answers', 'incorrect_answers', 'total_reviews', 'last_reviewed']
        read_only_fields = ['card', 'correct_answers', 'incorrect_answers', 'total_reviews', 'last_reviewed']