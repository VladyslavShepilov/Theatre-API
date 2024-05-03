from django.contrib.auth import get_user_model
from django.db import models


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


class Play(models.Model):
    title = models.CharField(max_length=255, unique=True)
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
        return f"{self.play.title} at {str(self.show_time)}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE)


class Reservation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
