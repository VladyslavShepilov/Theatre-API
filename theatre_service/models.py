import os
import uuid
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        unique_together = ("first_name", "last_name")
        ordering = ["last_name"]

    def __str__(self):
        return f"{self.full_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.name}"


def play_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/plays/", filename)


class Play(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = models.ImageField(null=True, upload_to=play_image_file_path)
    description = models.TextField(max_length=1000)
    duration = models.IntegerField(blank=True, null=True)
    actors = models.ManyToManyField(Actor, related_name="plays")
    genres = models.ManyToManyField(Genre, related_name="plays")

    def __str__(self):
        return f"{self.title}"


class TheatreHall(models.Model):
    name = models.CharField(max_length=255, unique=True)
    seats_in_row = models.PositiveIntegerField()
    rows = models.PositiveIntegerField()

    @property
    def capacity(self) -> int:
        return self.seats_in_row * self.rows

    def __str__(self):
        return f"{self.name}"


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["-show_time"]
        unique_together = ("play", "show_time", "theatre_hall")

    def __str__(self):
        return f"{self.play.title} at {self.show_time.strftime('%Y-%m-%d %H:%M')}"


class Reservation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        ordering = ["reservation"]
        unique_together = ("row", "seat", "performance")

    @staticmethod
    def validate_tickets(row, seat, theatre_hall, error_to_raise):
        for ticket_attr_value, ticket_attr_name, theatre_hall_attr_name in [
                (row, "row", "rows",),
                (seat, "seat", "seats_in_row")
        ]:
            theatre_hall_attr_value = getattr(theatre_hall, theatre_hall_attr_name)
            if not (1 <= ticket_attr_value <= theatre_hall_attr_value):
                raise error_to_raise(
                    f"{ticket_attr_name} with value {ticket_attr_name}"
                    f"must be in range from 1 to {theatre_hall_attr_value}"
                )

    def clean(self):
        Ticket.validate_tickets(
            self.row,
            self.seat,
            self.performance.theatre_hall,
            ValidationError
        )

    def __str__(self):
        return f"{self.row} {self.seat}"
