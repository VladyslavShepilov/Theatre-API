from datetime import datetime

from django.db.models import F, Count, Q
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer, ReservationListSerializer, ReservationDetailSerializer, PlayImageSerializer,
)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    def get_queryset(self):
        queryset = self.queryset
        word = self.request.query_params.get("actors")
        if word:
            queryset = queryset.filter(
                Q(first_name__icontains=word)
                & Q(last_name__icontains=word))
        return queryset


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_queryset(self):
        queryset = self.queryset
        title = self.request.query_params.get("genre")
        if title:
            queryset = queryset.filter(name__icontains=title)
        return queryset


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("actors", "genres")
    serializer_class = PlaySerializer

    def get_queryset(self):
        queryset = self.queryset
        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        elif self.action == "retrieve":
            return PlayDetailSerializer
        elif self.action == "upload_image":
            return PlayImageSerializer
        return PlaySerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific play"""
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = (
        Performance.objects
        .select_related("play", "theatre_hall")
        .annotate(
            tickets_available=(
                F("theatre_hall__rows")
                * F("theatre_hall__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        date = self.request.query_params.get("date")
        play_id_str = self.request.query_params.get("play")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(show_time__date=date)

        if play_id_str:
            queryset = queryset.filter(play_id=int(play_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        elif self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related("tickets__performance", "tickets__reservation")
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        elif self.action == "retrieve":
            return ReservationDetailSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
