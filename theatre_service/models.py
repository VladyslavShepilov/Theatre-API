from django.contrib.auth import get_user_model
from django.db import models


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Genre(models.Model):
    name = models.CharField(max_length=255)


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    seats_in_row = models.IntegerField()
    rows = models.IntegerField()


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)
    show_time = models.DateTimeField()


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE)


class Reservation(models.Model):
    user = models.ForeignKey(get_user_model(), )
    created_at = models.DateTimeField(auto_now_add=True)
