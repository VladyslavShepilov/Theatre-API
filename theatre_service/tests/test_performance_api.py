import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre_service.models import Performance, Play, TheatreHall
from theatre_service.tests.test_actor_api import sample_actor
from theatre_service.tests.test_theatre_hall_api import sample_theatre_hall
from theatre_service.tests.test_genre_api import sample_genre
from theatre_service.tests.test_play_api import sample_play
from theatre_service.serializers import PerformanceDetailSerializer

PERFORMANCE_URL = reverse("theatre-api:performance-list")


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


def create_staff_user(**kwargs):
    return get_user_model().objects.create_user(is_staff=True, **kwargs)


def sample_performance(**params):
    genres = sample_genre()
    actors = sample_actor()
    play = sample_play()

    play.genres.add(genres)
    play.actors.add(actors)

    theatre_hall = sample_theatre_hall()

    defaults = {
        "play": play,
        "theatre_hall": theatre_hall,
        "show_time": datetime.datetime(
            year=2022,
            month=9,
            day=2,
        ),
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def detail_url(performance_id):
    return reverse("theatre-api:performance-detail", args=[performance_id])


class PublicPerformanceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PERFORMANCE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePerformanceApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            username="test_user",
            email="test@test.com",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_performances(self):
        sample_performance()

        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_performances(self):
        performance = sample_performance()

        url = detail_url(performance.id)
        response = self.client.get(url)

        serializer = PerformanceDetailSerializer(performance)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_post_performance(self):
        response = self.client.post(PERFORMANCE_URL, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_performance(self):
        performance = sample_performance()

        url = detail_url(performance.id)
        response = self.client.put(url, {})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_performance(self):
        performance = sample_performance()

        url = detail_url(performance.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminPerformanceApiTests(TestCase):
    def setUp(self):
        self.user = create_staff_user(
            username="admin",
            email="admin@test.com",
            password="adminpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_post_performance(self):
        genres = sample_genre()
        actors = sample_actor()
        play = sample_play()

        play.genres.add(genres)
        play.actors.add(actors)

        theatre_hall = sample_theatre_hall()

        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": datetime.datetime(
                year=2023,
                month=1,
                day=23,
            ),
        }

        response = self.client.post(PERFORMANCE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_performance(self):
        performance = sample_performance()

        play = Play.objects.first()
        theatre_hall = TheatreHall.objects.first()

        payload = {
            "play": play.id,
            "theatre_hall": theatre_hall.id,
            "show_time": datetime.datetime(
                year=2022,
                month=9,
                day=2,
            ),
        }

        url = detail_url(performance.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_performance(self):
        performance = sample_performance()

        url = detail_url(performance.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
