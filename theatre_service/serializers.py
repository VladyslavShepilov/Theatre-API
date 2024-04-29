from rest_framework import serializers
from theatre_service.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation,
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name",)


class PlayListSerializer(serializers.ModelSerializer):
    actors = serializers.SlugRelatedField(
        slug_field="actors__full_name",
        many=True,
        read_only=True
    )
    genres = serializers.SlugRelatedField(
        slug_field="genres__name",
        many=True,
        read_only=True
    )

    class Meta:
        model = Play
        fields = ("title", "description", "actors", "genres")


class PlayDetailSerializer(serializers.ModelSerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ("title", "description", "actors", "genres")
