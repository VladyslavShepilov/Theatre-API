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
        fields = ("id", "first_name", "last_name", "full_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name",)


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("title", "description", "duration", "actors", "genres")


class PlayListSerializer(serializers.ModelSerializer):
    actors = serializers.SlugRelatedField(
        slug_field="full_name",
        many=True,
        read_only=True
    )
    genres = serializers.SlugRelatedField(
        slug_field="name",
        many=True,
        read_only=True
    )

    class Meta:
        model = Play
        fields = ("title", "description", "duration", "actors", "genres")


class PlayDetailSerializer(serializers.ModelSerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ("title", "description", "duration", "actors", "genres")


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "seats_in_row", "rows", "capacity")
        read_only_fields = ("capacity",)


class TheatreHallListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "capacity")


class PerformanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Performance
        fields = ("play", "theatre_hall", "show_time")


class PerformanceListSerializer(serializers.ModelSerializer):
    play = serializers.SlugRelatedField(
        slug_field="title",
        read_only=True,
        many=False
    )
    theatre_hall = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        many=False
    )

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class PerformanceDetailSerializer(serializers.ModelSerializer):
    play = PlayListSerializer(read_only=True, many=False)
    theatre_hall = TheatreHallSerializer(read_only=True, many=False)

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")
