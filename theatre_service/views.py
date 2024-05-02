from django.db.models import F
from django.shortcuts import render
from rest_framework import viewsets, mixins

from theatre_service.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation,
)
from theatre_service.serializers import (
    ActorSerializer,
    GenreSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    TheatreHallSerializer,
    TheatreHallListSerializer,
)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("actors", "genres")
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer

    def get_queryset(self):
        queryset = self.queryset

        params = self.request.query_params
        name = params.get("name")
        capacity = params.get("capacity")

        if name:
            queryset = queryset.filter(name__icontains=name)
        """
        find the hall with requested capacity or higher
        """
        if capacity is not None and capacity.isdigit():
            capacity_int = int(capacity)
            queryset = queryset.annotate(
                size=F("seats_in_row") * F("rows")
            ).filter(size__gte=capacity_int)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TheatreHallListSerializer
        return TheatreHallSerializer
