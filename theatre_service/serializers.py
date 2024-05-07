from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        fields = ("title", "description", "duration", "actors", "genres", "image")


class PlayDetailSerializer(serializers.ModelSerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ("title", "description", "duration", "actors", "genres", "image")


class PlayImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "image")


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
    play_image = serializers.ImageField(source="play.image", read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time", "tickets_available", "play_image")


class PerformanceDetailSerializer(serializers.ModelSerializer):
    play = PlayListSerializer(read_only=True, many=False)
    theatre_hall = TheatreHallSerializer(read_only=True, many=False)

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat", "performance")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_tickets(
            row=attrs["row"],
            seat=attrs["seat"],
            theatre_hall=attrs["performance"].theatre_hall,
            error_to_raise=ValidationError
        )
        return data


class TicketListSerializer(serializers.ModelSerializer):
    performance = serializers.SlugRelatedField(slug_field="play__title", read_only=True)

    class Meta:
        model = Ticket
        fields = ("row", "seat", "performance")


class TicketDetailSerializer(serializers.Serializer):
    performance = PerformanceListSerializer(read_only=True, many=False)

    class Meta:
        model = Ticket
        fields = ("seat", "row", "performance")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_null=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        with transaction.atomic():
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "tickets")


class ReservationDetailSerializer(serializers.ModelSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "tickets")
